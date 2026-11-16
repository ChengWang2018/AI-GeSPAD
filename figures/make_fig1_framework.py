import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as spla
import matplotlib as mpl, matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.tri as mtri
from scipy.ndimage import gaussian_filter
rng=np.random.default_rng(7)
mpl.rcParams.update({'font.family':['Liberation Sans','DejaVu Sans'],'font.size':6.5,'axes.linewidth':0.5,
 'xtick.major.width':0.5,'ytick.major.width':0.5,'xtick.major.size':2,'ytick.major.size':2,
 'axes.labelsize':6.5,'xtick.labelsize':6,'ytick.labelsize':6,'legend.fontsize':5.8,'pdf.fonttype':42})
INK='#0b0b0b'; MUTE='#52514e'; BLUE='#2a78d6'; ORANGE='#eb6834'; AQUA='#1baf7a'
C_SI='#c9c8c3'; C_GE='#eda100'; C_OX='#d6e6f5'; C_MET='#6b6a66'; C_NP='#8fb7e8'; C_PS='#f2a07b'
seq=LinearSegmentedColormap.from_list('seq',['#fbf8f2','#f6d8a8','#eb6834','#9c2a0b','#3d0d02'])
seqb=LinearSegmentedColormap.from_list('seqb',['#f7f9fc','#a9c8ee','#2a78d6','#0d3a75'])

# ---------------- Poisson solve on 2D cross-section (units: um, V) ----------------
h=0.01; X0,X1,Y1=0,4.0,2.2
nx,ny=int(X1/h)+1,int(Y1/h)+1
x=np.linspace(0,X1,nx); y=np.linspace(0,Y1,ny); XX,YY=np.meshgrid(x,y)
GE=(XX>=1.0)&(XX<=3.0)&(YY>=1.0)&(YY<=1.55)
SI=(YY<1.0)
OX=~(GE|SI)
eps=np.where(GE,16.0,np.where(SI,11.7,3.9))
N=np.zeros_like(XX); cs=(YY>=0.78)&(YY<=0.83)&(XX>=0.85)&(XX<=3.15); N[cs]=-4.2e17*1e-12  # p charge sheet, um^-3
rho_eps0=1.6e-19*N/8.854e-18   # V/um^2
idx=np.arange(nx*ny).reshape(ny,nx)
V=34.0
dir_mask=np.zeros_like(XX,bool); dir_val=np.zeros_like(XX)
dir_mask[0,:]=True; dir_val[0,:]=V
top=(np.abs(YY-1.55)<h/2)&(XX>=1.0)&(XX<=3.0); dir_mask|=top
rows=[];cols=[];vals=[];b=np.zeros(nx*ny)
def ea(a,b_): return 2*a*b_/(a+b_)
for j in range(ny):
  for i in range(nx):
    k=idx[j,i]
    if dir_mask[j,i]:
      rows.append(k);cols.append(k);vals.append(1.0);b[k]=dir_val[j,i];continue
    diag=0.0
    for dj,di in((0,1),(0,-1),(1,0),(-1,0)):
      jj,ii=j+dj,i+di
      if jj<0 or jj>=ny or ii<0 or ii>=nx: continue
      c=ea(eps[j,i],eps[jj,ii])
      rows.append(k);cols.append(idx[jj,ii]);vals.append(c);diag-=c
    rows.append(k);cols.append(k);vals.append(diag)
    b[k]=-rho_eps0[j,i]*h*h
A=sp.csr_matrix((vals,(rows,cols)),shape=(nx*ny,nx*ny))
phi=spla.spsolve(A,b).reshape(ny,nx)
Ey,Ex=np.gradient(-phi,h,h); E=np.hypot(Ex,Ey)*10  # kV/cm
E[OX]=np.nan
print('E Si mult max %.0f, Ge mean %.0f kV/cm'%(np.nanmax(E[(YY<0.78)&(YY>0.3)]),np.nanmean(E[GE])))



from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon
W,H=17.0/2.54,8.8/2.54
fig=plt.figure(figsize=(W,H))
GRAYH='#6b6a66'
def module(x0,y0,x1,y1,head,hc,body_txt,tx=0.008,ty=None,fs=5.5):
    fig.add_artist(FancyBboxPatch((x0,y0),x1-x0,y1-y0,boxstyle='round,pad=0.0,rounding_size=0.008',transform=fig.transFigure,fc='white',ec=hc,lw=0.8,zorder=-2))
    hh=0.062
    fig.add_artist(FancyBboxPatch((x0,y1-hh),x1-x0,hh,boxstyle='round,pad=0.0,rounding_size=0.008',transform=fig.transFigure,fc=hc,ec=hc,lw=0.8,zorder=-1))
    fig.text(x0+0.008,y1-hh/2,head,color='white',fontsize=6.3,fontweight='bold',va='center')
    if body_txt: fig.text(x0+tx,(y1-hh-0.012) if ty is None else ty,body_txt,fontsize=fs,va='top',color=INK,linespacing=1.25)
def arrow(p,q,label=None,lpos=None,ha='center',va='center',color=INK,rad=0.0,ls='-',fs=5.2,lw=0.8):
    fig.add_artist(FancyArrowPatch(p,q,transform=fig.transFigure,arrowstyle='-|>',mutation_scale=6,lw=lw,color=color,connectionstyle=f'arc3,rad={rad}',linestyle=ls,shrinkA=0,shrinkB=0))
    if label:
        lp=lpos if lpos else ((p[0]+q[0])/2,(p[1]+q[1])/2)
        fig.text(lp[0],lp[1],label,fontsize=fs,ha=ha,va=va,color=color,linespacing=1.15)
def thumb(rect): 
    a=fig.add_axes(rect); a.set_xticks([]); a.set_yticks([])
    for sp_ in a.spines.values(): sp_.set_linewidth(0.4); sp_.set_color('#9a9994')
    return a
C1,C2,C3,C4,C5='#3d3c39','#2a78d6','#1baf7a','#eb6834','#6250d6'

# ---- banner: core problem ----
fig.add_artist(FancyBboxPatch((0.215,0.905),0.60,0.085,boxstyle='round,pad=0.0,rounding_size=0.01',transform=fig.transFigure,fc='#f4f3ef',ec='none',zorder=-2))
fig.text(0.515,0.962,r'Core problem:  $\max_{\mathbf{x}\in\mathcal{X}}\ \min_{\boldsymbol{\delta}\in\Delta}\ \rho(\mathbf{x},\boldsymbol{\delta})$   subject to a TCAD budget $\sum_\ell n_\ell c_\ell\leq B$',ha='center',va='center',fontsize=7.0)
fig.text(0.515,0.924,'designer ③ maximises over designs x  ·  challenger ④ minimises over uncertainties δ  ·  all claims checked by TCAD ①',ha='center',va='center',fontsize=5.4,color=MUTE)

# ---- inputs ----
module(0.005,0.03,0.172,0.89,'Domain challenge',C1,
 'Target (1550 nm, 230 K):\n  SPDE ≥ $\\eta^*$,  DCR ≤ $D^*$\nDesign $\\mathbf{x}$: geometry, doping, $V$\nUncertain $\\boldsymbol{\\delta}$: $\\boldsymbol{\\theta}$, process, $\\Delta V$\nData: HWU SPADs, TCAD',fs=5.2)
import os
_D=os.path.dirname(os.path.abspath(__file__))
def _img(name): return plt.imread(os.path.join(_D,name))
# real device cross-section (team's preliminary TCAD)
a=fig.add_axes([0.012,0.585,0.156,0.09]); a.imshow(_img('cen_device.png')); a.axis('off')
fig.text(0.0885,0.572,'lateral Ge/Si waveguide APD (TCAD)',fontsize=4.5,ha='center',color=MUTE)
fig.text(0.014,0.235,'Preliminary TCAD (team):\n• $V_\\mathrm{bd}$ within 7% of a published\n   device\n• $W_P$ 130→170 nm shifts $V_\\mathrm{bd}$\n   from −16 V to −8 V',fontsize=4.8,va='top',color=INK,linespacing=1.25)
t=fig.add_axes([0.012,0.285,0.158,0.235]); t.imshow(_img('cen_iv.png')); t.axis('off')
fig.text(0.0885,0.527,'$W_P$ sweep: breakdown shift',fontsize=4.6,ha='center',color=MUTE)

# ---- ① physics & data engine ----
module(0.215,0.565,0.815,0.885,'①  Physics & data engine  ·  WP1 (Xin)',C1,
 'Automated Silvaco TCAD: 2D screening, 3D\nverification. The ground truth for every claim.\n\nBayesian calibration to measured devices\n→ posterior $p(\\boldsymbol{\\theta}\\,|\\,\\mathrm{data})$ on impact-\nionisation & defect parameters.')
t=thumb([0.515,0.59,0.135,0.195])
# synthetic mesh on the team's lateral Ge/Si waveguide APD geometry
def matof(x,y):
    if 3.1<=x<=3.7 and 2.2<=y<=2.4: return 2            # Ge
    if 2.0<=y<=2.2: return 1                             # Si slab
    if 2.2<y<=2.3 and (x<2.1 or x>4.9): return 1         # Si contact regions
    if 2.3<y<=2.4 and (x<2.1 or x>4.9): return 3         # Al
    return 0                                             # SiO2
pts=[]
for _ in range(2200):
    px_=rng.uniform(1.6,5.4); py_=rng.uniform(1.85,2.55)
    d=min(abs(py_-2.0),abs(py_-2.2),abs(py_-2.4)+(0 if 3.1<=px_<=3.7 else 1),abs(px_-3.1)+(0 if 2.2<=py_<=2.4 else 1),abs(px_-3.7)+(0 if 2.0<=py_<=2.4 else 1),abs(px_-3.85)+(0 if 2.0<=py_<=2.2 else 1))
    if rng.uniform()<np.exp(-d/0.04)+0.015: pts.append((px_,py_))
for gx in np.linspace(1.6,5.4,16):
    for gy in [1.85,2.0,2.2,2.4,2.55]: pts.append((gx,gy))
for gx in np.linspace(3.1,3.7,8): pts.append((gx,2.4))
for gy in np.linspace(2.2,2.4,4): pts+=[(3.1,gy),(3.7,gy)]
pts=np.array(pts); tri=mtri.Triangulation(pts[:,0],pts[:,1]); cx=pts[tri.triangles].mean(1)
mat=np.array([matof(a_,b_) for a_,b_ in cx])
t.tripcolor(tri,facecolors=mat,cmap=mpl.colors.ListedColormap([C_OX,C_SI,C_GE,'#d9a6a0']),vmin=-0.5,vmax=3.5); t.triplot(tri,color='#5d5c58',lw=0.08)
t.set_xlim(1.6,5.4); t.set_ylim(1.85,2.55); t.set_title('TCAD mesh → graph',fontsize=5,pad=1.5)
t=fig.add_axes([0.695,0.62,0.105,0.16])
vb=np.linspace(0.5,5,50); m=2e3*np.exp(0.75*vb); t.fill_between(vb,m*0.55,m*1.8,color=C2,alpha=0.2,lw=0); t.plot(vb,m,color=C2,lw=0.8)
vm=np.array([1,1.8,2.6,3.4,4.2]); t.scatter(vm,2e3*np.exp(0.75*vm)*np.exp(rng.normal(0,0.25,5)),s=5,c=INK,zorder=3)
t.set_yscale('log'); t.tick_params(labelsize=4.5,length=1.5,width=0.4,pad=1); t.set_xlabel('excess bias (V)',fontsize=4.8,labelpad=0.5); t.set_ylabel('DCR',fontsize=4.8,labelpad=0.5)
t.set_title('calibration: data vs posterior',fontsize=5,pad=1.5); t.spines[['top','right']].set_visible(False)
for sp_ in t.spines.values(): sp_.set_linewidth(0.4)

# ---- bottom row: ④ challenger, ③ designer, ② surrogate ----
Y0,Y1=0.03,0.42
module(0.215,Y0,0.39,Y1,'④  Challenger · WP3',C4,'Adversarial search over $\\Delta$\n$\\boldsymbol{\\delta}^*=\\mathrm{arg\\,min}\\,\\rho(\\mathbf{x}^*,\\boldsymbol{\\delta})$;\nestimates $P_\\mathrm{fail}$;\nthen 250–295 K sweep',fs=5.3)
module(0.43,Y0,0.60,Y1,'③  Designer · WP2',C3,'Robust multi-objective BO:\nchooses next $(\\mathbf{x},\\ell)$;\nmaximises worst-case $\\rho$',fs=5.3)
module(0.64,Y0,0.815,Y1,'②  Graph surrogate · WP2',C2,'GNN ensemble on mesh →\nfield maps → physics layer\n→ SPDE, DCR, $g$  ($\\mu\\pm\\sigma$)',fs=5.3)
# ④ thumb: falsification
t=thumb([0.228,0.045,0.15,0.165])
u=np.linspace(-15,15,150); v=np.linspace(-50,50,150); U,Vt=np.meshgrid(u,v); Vv=262.5+0.65*Vt
mg=1.0-((U+2)/11)**2-((Vv-250)/48)**2-0.8*np.exp(-(((U-8.5)/3.5)**2+((Vv-285)/9)**2))
t.imshow(mg,origin='lower',extent=[-15,15,-50,50],aspect='auto',cmap='RdBu',norm=TwoSlopeNorm(0,-1.5,1),alpha=0.7)
t.contour(U,Vt,mg,levels=[0],colors=INK,linewidths=0.5)
mc=np.c_[rng.normal(-1,4.5,35),(rng.normal(255,12,35)-262.5)/0.65]; t.scatter(mc[:,0],mc[:,1],s=1.5,c='#4a4945',lw=0)
pth=np.array([[0,255],[3,265],[5.5,274],[7.2,280],[8.2,283.5],[8.7,285]]); pth[:,1]=(pth[:,1]-262.5)/0.65; t.plot(pth[:,0],pth[:,1],color=C4,lw=0.7); t.scatter(pth[:,0],pth[:,1],s=4,c=C4,zorder=3)
t.scatter([8.7],[(285-262.5)/0.65],s=18,marker='X',c='#c4161c',edgecolors='white',lw=0.3,zorder=4)
t.set_xlim(-15,15); t.set_ylim(-50,50)
fig.text(0.303,0.215,'Δ $W_P$ (process) ↔ Δ trap density',fontsize=4.6,ha='center',color=MUTE)
# ③ thumb: robust Pareto
t=thumb([0.443,0.045,0.145,0.165])
fx=np.logspace(3,6.4,60); fr=55*(1-np.exp(-(np.log10(fx)-2.7)/1.3)); rb=fr-6-4*np.exp(-((np.log10(fx)-4.3)/0.8)**2)
t.plot(fx,fr,color=MUTE,lw=0.7,ls='--'); t.plot(fx,rb,color=C3,lw=1.0)
d3=10**np.array([3.5,4.0,4.5,5.0,5.6]); t.scatter(d3,55*(1-np.exp(-(np.log10(d3)-2.7)/1.3))-6.5+rng.normal(0,1,5),s=5,c=C3,zorder=3)
t.set_xscale('log'); t.set_ylim(0,62); t.set_xticks([]); t.set_yticks([]); t.minorticks_off()
t.text(10**3.1,52,'nominal',fontsize=4.4,color=MUTE); t.text(10**5.0,12,'robust front',fontsize=4.4,color=C3)
fig.text(0.515,0.215,'SPDE  vs  DCR',fontsize=4.6,ha='center',color=MUTE)
# ② thumb: field
t=fig.add_axes([0.653,0.045,0.15,0.165]); t.imshow(_img('cen_field.png')); t.axis('off')
fig.text(0.728,0.215,'|E| map (ATLAS, team)',fontsize=4.6,ha='center',color=MUTE)

# ---- ⑤ explain & outputs ----
module(0.853,0.315,0.995,0.885,'⑤ Explain · WP4',C5,'Field attribution,\nSHAP, symbolic\nregression → rules;\nblind 3D validation',fs=5.3)
t=fig.add_axes([0.895,0.345,0.09,0.25]); t.set_title('|SHAP|',fontsize=4.6,pad=1); vals=[0.8,0.66,0.52,0.93,0.74]; t.barh(np.arange(5),vals,color=C5,height=0.6)
t.set_xticks([]); t.set_yticks(range(5)); t.set_yticklabels(['dose','width','$t_\\mathrm{Ge}$','T','traps'],fontsize=4.3); t.tick_params(length=0,pad=1)
for sp_ in t.spines.values(): sp_.set_visible(False)
module(0.853,0.03,0.995,0.275,'Outputs',C1,'• Robust front &\n   shortlist\n• Design rules\n• Open toolkit\n• GeSPAD-Bench\n• Fab. roadmap',fs=5.3)

# ---- arrows ----
arrow((0.172,0.75),(0.215,0.75),'template,\ndata',(0.1935,0.80),fs=4.8)
arrow((0.172,0.30),(0.215,0.30),'specs\n$\\eta^*,D^*$',(0.1935,0.355),fs=4.8)
arrow((0.735,0.565),(0.735,0.42),'mesh graphs + fields\n2D pre-train → 3D fine-tune',(0.728,0.492),ha='right',fs=4.9)
arrow((0.64,0.25),(0.60,0.25),'$\\mu\\pm\\sigma$',(0.62,0.275),fs=5.0)
arrow((0.515,0.42),(0.515,0.565),'query $(\\mathbf{x},\\ell)$\n2D / 3D',(0.522,0.492),ha='left',fs=4.9)
arrow((0.43,0.29),(0.39,0.29),'$\\mathbf{x}^*$',(0.41,0.315),fs=5.2)
arrow((0.39,0.20),(0.43,0.20),'$\\boldsymbol{\\delta}^*,\\rho$',(0.41,0.175),fs=5.0,color=C4)
arrow((0.26,0.565),(0.26,0.42),'$\\Delta$ from\n$p(\\boldsymbol{\\theta}|\\mathrm{data})$',(0.253,0.492),ha='right',fs=4.9)
arrow((0.33,0.42),(0.33,0.565),'simulate\n$(\\mathbf{x}^*,\\boldsymbol{\\delta}^*)$',(0.337,0.492),ha='left',fs=4.9,color=C4)
arrow((0.815,0.36),(0.853,0.36),'robust\ndesigns',(0.834,0.40),fs=4.6)
arrow((0.924,0.315),(0.924,0.275))
# loop label
fig.text(0.445,0.455,'robust design loop',fontsize=5.2,ha='center',va='center',style='italic',color=MUTE)
fig.savefig('/mnt/user-data/outputs/Fig1_AI-GeSPAD.pdf'); fig.savefig('/tmp/claude-0/fig/Fig1.png',dpi=300)
