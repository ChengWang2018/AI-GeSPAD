import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as spla
import matplotlib as mpl, matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.tri as mtri
from scipy.ndimage import gaussian_filter
rng=np.random.default_rng(7)
mpl.rcParams.update({'font.family':'Liberation Sans','font.size':6.5,'axes.linewidth':0.5,
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


W,H=17.0/2.54,9.4/2.54
fig=plt.figure(figsize=(W,H))
def title(x,y,l,t):
    fig.text(x,y,l,fontsize=8.5,fontweight='bold',va='baseline'); fig.text(x+0.022,y,t,fontsize=6.6,va='baseline')
SPINES=lambda ax: ax.spines[['top','right']].set_visible(False)

# ---------------- a: oblique-projection device (painter's order) ----------------
ax=fig.add_axes([0.0,0.50,0.375,0.40]); ax.set_aspect('equal'); ax.axis('off')
th=np.deg2rad(32); ky=0.55; zs=1.9
def P(x,y,z): return (x+ky*y*np.cos(th), zs*z+ky*y*np.sin(th))
def box(x0,x1,y0,y1,z0,z1,c,lw=0.3):
    rgb=np.array(mpl.colors.to_rgb(c))
    faces=[([(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)],1.0),      # top
           ([(x0,y0,z0),(x1,y0,z0),(x1,y0,z1),(x0,y0,z1)],0.86),     # front
           ([(x1,y0,z0),(x1,y1,z0),(x1,y1,z1),(x1,y0,z1)],0.72)]     # right
    for f,sh in faces:
        ax.add_patch(mpl.patches.Polygon([P(*q) for q in f],closed=True,fc=np.clip(rgb*sh,0,1),ec='#3a3a38',lw=lw,joinstyle='round'))
box(0,8,0,4,0,0.3,'#dcdbd6'); box(0,8,0,4,0.3,0.6,C_OX)
box(3.0,8,2.95,3.2,0.6,1.05,C_MET)                    # back side contact
box(0,3.0,1.55,2.45,0.6,0.85,C_SI)                    # Si rib waveguide
box(3.0,8,0.8,2.95,0.6,0.85,'#b8b7b1')                # Si multiplication slab
box(3.0,8,1.2,2.8,0.85,0.9,C_PS)                      # p charge sheet
box(3.4,7.6,1.4,2.6,0.9,1.45,C_GE)                    # Ge absorber
box(3.8,7.2,1.75,2.25,1.45,1.53,C_MET)                # top contact
# photon + guided mode
xs=np.linspace(-2.3,0.0,90); px,py=zip(*[P(x,2.0,0.73) for x in xs]); py=np.array(py)+0.16*np.sin(xs*9)
ax.plot(px,py,color='#c4161c',lw=1.0); a_=P(0.0,2.0,0.73)
ax.annotate('',xy=(a_[0]+0.35,a_[1]),xytext=a_,arrowprops=dict(arrowstyle='-|>',color='#c4161c',lw=0.9,mutation_scale=6))
ax.text(*P(-2.6,2.0,1.15),'1550 nm photon',color='#c4161c',fontsize=5.8)
def lab(p,q,s,ha='left'):
    a=P(*p); ax.plot([a[0],q[0]],[a[1],q[1]],color=MUTE,lw=0.35); ax.text(q[0]+(0.08 if ha=='left' else -0.08),q[1],s,fontsize=5.6,va='center',ha=ha,color=INK)
lab((4.2,1.4,1.3),(0.6,3.9),'Ge absorber (L, t$_\\mathrm{Ge}$, w)',ha='left')
lab((7.0,2.0,1.53),(8.6,4.0),'p$^+$ contact')
lab((8.0,1.5,0.88),(10.0,2.75),'charge sheet (dose)')
lab((8.0,1.0,0.75),(10.0,1.95),'Si multiplication')
lab((1.4,1.55,0.8),(0.6,-0.45),'Si rib waveguide')
lab((8.0,0.2,0.3),(10.0,1.05),'SiO$_2$ / Si')
ax.set_xlim(-2.8,13.6); ax.set_ylim(-0.9,4.4)
title(0.012,0.935,'a','Device and design space $\\mathbf{x}$ (geometry, doping, $V$, $T$)')

# ---------------- b: mesh -> graph ----------------
ax=fig.add_axes([0.435,0.565,0.215,0.33])
pts=[]
for _ in range(5200):
    px=rng.uniform(0,4); py=rng.uniform(0,2.2)
    d=min(abs(py-1.0),abs(py-0.8),abs(py-1.55)+(0 if 1<=px<=3 else 2),abs(px-1.0)+(0 if 1<=py<=1.55 else 2),abs(px-3.0)+(0 if 1<=py<=1.55 else 2))
    if rng.uniform()<np.exp(-d/0.12)+0.05: pts.append((px,py))
# boundary-conforming nodes
for gx in np.linspace(0,4,21):
    for gy in [0,0.8,1.0,2.2]: pts.append((gx,gy))
for gx in np.linspace(1,3,15): pts.append((gx,1.55))
for gy in np.linspace(1,1.55,6): pts+= [(1.0,gy),(3.0,gy)]
for gy in np.linspace(0,2.2,9): pts+= [(0,gy),(4,gy)]
pts=np.array(pts); tri=mtri.Triangulation(pts[:,0],pts[:,1]); cx=pts[tri.triangles].mean(1)
mat=np.where((cx[:,0]>=1)&(cx[:,0]<=3)&(cx[:,1]>=1)&(cx[:,1]<=1.55),2,np.where(cx[:,1]<1,1,0))
mat[(cx[:,1]>=0.78)&(cx[:,1]<=0.86)]=3
cm=mpl.colors.ListedColormap([C_OX,C_SI,C_GE,C_PS])
ax.tripcolor(tri,facecolors=mat,cmap=cm,vmin=-0.5,vmax=3.5,edgecolors='none'); ax.triplot(tri,color='#5d5c58',lw=0.1)
ax.set_xlim(0,4); ax.set_ylim(0,2.2); ax.set_aspect('equal'); ax.set_xticks([0,2,4]); ax.set_yticks([0,1,2])
ax.set_xlabel('x (µm)',labelpad=1); ax.set_ylabel('y (µm)',labelpad=1)
ins=fig.add_axes([0.665,0.70,0.075,0.17])
sel=(pts[:,0]>2.8)&(pts[:,0]<3.2)&(pts[:,1]>0.9)&(pts[:,1]<1.2); P=pts[sel]; t2=mtri.Triangulation(P[:,0],P[:,1])
ins.triplot(t2,color='#4a4945',lw=0.3)
nc=np.where((P[:,0]<=3)&(P[:,1]>=1),C_GE,np.where(P[:,1]<1,'#9d9c97',C_OX))
ins.scatter(P[:,0],P[:,1],s=4,c=nc,edgecolors=INK,linewidths=0.25,zorder=3); ins.set_xticks([]);ins.set_yticks([])
for sp_ in ins.spines.values(): sp_.set_linewidth(0.5)
ax.indicate_inset_zoom(ins,edgecolor=INK,lw=0.4,alpha=1)
fig.text(0.665,0.645,'nodes: material,\n  doping, position\nedges: $\\Delta\\mathbf{r}$\nglobal: $V$, $T$',fontsize=5.2,va='top',color=INK)
title(0.405,0.935,'b','Mesh → graph input')

# ---------------- c: GNN predicted field ----------------
ax=fig.add_axes([0.775,0.565,0.18,0.33])
im=ax.imshow(E,origin='lower',extent=[0,4,0,2.2],cmap=seq,vmin=0,vmax=400,interpolation='bilinear'); ax.set_facecolor('#eef3f9')
for m in (GE,SI): ax.contour(XX,YY,m.astype(float),levels=[0.5],colors=INK,linewidths=0.4)
ax.set_aspect('equal'); ax.set_xticks([0,2,4]); ax.set_yticks([0,1,2]); ax.set_xlabel('x (µm)',labelpad=1)
cax=fig.add_axes([0.962,0.60,0.008,0.26]); cb=fig.colorbar(im,cax=cax); cb.outline.set_linewidth(0.4)
cb.ax.tick_params(width=0.4,length=1.5,labelsize=5.3); cb.set_ticks([0,200,400])
fig.text(0.962,0.875,'|E|\nkV/cm',fontsize=5.2,ha='left')
ax.text(2.0,0.45,'avalanche region',fontsize=5.2,ha='center',color='white')
ax.annotate('corner\nfield',xy=(1.0,1.0),xytext=(0.12,1.62),fontsize=5.2,arrowprops=dict(arrowstyle='-',lw=0.4))
ins=ax.inset_axes([0.62,0.63,0.38,0.37]); G=np.nan_to_num(E); unc=gaussian_filter(np.hypot(*np.gradient(G)),6); unc[OX]=np.nan
ins.imshow(unc,origin='lower',extent=[0,4,0,2.2],cmap=seqb,interpolation='bilinear'); ins.set_xticks([]);ins.set_yticks([]); ins.set_facecolor('white')
for sp_ in ins.spines.values(): sp_.set_linewidth(0.4)
ins.text(0.05,0.9,'ensemble σ',transform=ins.transAxes,fontsize=4.8,va='top')
title(0.745,0.935,'c','Graph surrogate → physics layer')

# ---------------- d: Pareto ----------------
ax=fig.add_axes([0.065,0.10,0.255,0.29]); SPINES(ax)
d2=10**rng.uniform(3.2,6.3,160); s2=np.clip(55*(1-np.exp(-(np.log10(d2)-2.7)/1.3))-rng.exponential(11,160),1,None)
ax.scatter(d2,s2,s=3,c='#b9b8b3',lw=0,label='2D TCAD (screening)')
fx=np.logspace(3.0,6.4,80); front=55*(1-np.exp(-(np.log10(fx)-2.7)/1.3)); band=2.5+3.5*np.exp(-((np.log10(fx)-4.4)/0.9)**2)
ax.fill_between(fx,front-band,front+band,color=BLUE,alpha=0.18,lw=0); ax.plot(fx,front,color=BLUE,lw=1.0,label='predicted Pareto front ± σ')
d3=10**np.array([3.4,3.8,4.1,4.5,4.9,5.3,5.8]); s3=55*(1-np.exp(-(np.log10(d3)-2.7)/1.3))+rng.normal(0,1.5,7)
ax.scatter(d3,s3,s=13,c=BLUE,edgecolors='white',linewidths=0.6,zorder=4,label='3D TCAD (verified)')
dn=10**np.array([3.15,3.6,4.3]); sn=55*(1-np.exp(-(np.log10(dn)-2.7)/1.3))+np.array([4,3.5,2.5])
ax.scatter(dn,sn,s=15,marker='D',facecolors='none',edgecolors=ORANGE,linewidths=0.8,zorder=5,label='next batch (acquisition)')
ax.scatter([10**5.1],[21],s=26,marker='*',c=INK,zorder=5,label='reference design')
ax.set_xscale('log'); ax.set_xlabel('Dark count rate (s$^{-1}$)',labelpad=1); ax.set_ylabel('SPDE at 1550 nm (%)',labelpad=1); ax.set_ylim(0,80)
ax.legend(frameon=False,loc='upper left',ncol=2,handlelength=1.0,columnspacing=0.6,borderaxespad=0.0,labelspacing=0.2,fontsize=5.0)
title(0.012,0.455,'d','Design: multi-objective Bayesian optimisation')

# ---------------- e: falsification ----------------
ax=fig.add_axes([0.405,0.10,0.235,0.29])
u=np.linspace(-20,20,200); v=np.linspace(-60,60,200); U,Wv=np.meshgrid(u,v)
margin=1.0-((U+4)/14)**2-((Wv-8)/55)**2-0.75*np.exp(-(((U-11)/4)**2+((Wv+38)/14)**2))
ax.imshow(margin,origin='lower',extent=[-20,20,-60,60],aspect='auto',cmap='RdBu',norm=TwoSlopeNorm(0,-1.5,1),alpha=0.7,interpolation='bilinear')
ax.contour(U,Wv,margin,levels=[0],colors=INK,linewidths=0.6)
mc=np.c_[rng.normal(-1,5.5,55),rng.normal(2,17,55)]
ax.scatter(mc[:,0],mc[:,1],s=3,c='#4a4945',lw=0,label='random Monte Carlo')
path=np.array([[2,10],[6,-5],[9,-20],[11,-30],[11.5,-36],[12.2,-39],[12.6,-40.5]])
ax.plot(path[:,0],path[:,1],color=ORANGE,lw=0.8); ax.scatter(path[:,0],path[:,1],s=8,c=ORANGE,edgecolors='white',lw=0.4,zorder=4,label='adversarial search')
ax.scatter([12.6],[-40.5],s=36,marker='X',c='#c4161c',edgecolors='white',lw=0.4,zorder=5)
ax.text(-1.5,-56,'hidden edge-breakdown failure',fontsize=5.0,ha='center',color=INK)
ax.text(-4,15,'spec met',fontsize=5.4,ha='center',color=INK)
ax.set_xlabel('Δ charge-sheet doping (%)',labelpad=1); ax.set_ylabel('Δ Ge thickness (nm)',labelpad=1)
ax.legend(frameon=True,facecolor='white',edgecolor='none',framealpha=0.85,loc='upper right',handlelength=0.9,borderaxespad=0.2,labelspacing=0.2,fontsize=5.0)
title(0.345,0.455,'e','Falsify: process & temperature variation')

# ---------------- f: explain ----------------
ax=fig.add_axes([0.80,0.10,0.185,0.29]); SPINES(ax)
feats=['Charge-sheet dose','Multiplication width','Ge thickness','Temperature','Interface traps','Waveguide width']
s_spde=np.array([0.62,0.48,0.71,0.12,0.05,0.55]); s_dcr=np.array([0.81,0.66,0.52,0.93,0.74,0.08]); yy=np.arange(6)[::-1]
ax.barh(yy+0.19,s_spde,height=0.34,color=BLUE,label='SPDE',edgecolor='white',lw=0.5)
ax.barh(yy-0.19,s_dcr,height=0.34,color=ORANGE,label='DCR',edgecolor='white',lw=0.5)
ax.set_yticks(yy); ax.set_yticklabels(feats,fontsize=5.6); ax.set_xlabel('mean |SHAP| (norm.)',labelpad=1); ax.set_xlim(0,1); ax.set_ylim(-0.6,6.3)
ax.legend(frameon=False,loc='upper right',ncol=2,columnspacing=0.8,handlelength=0.9,borderaxespad=0.0)
fig.text(0.665,0.415,'rule found: keep $E_\\mathrm{Ge}<E_\\mathrm{tun}(T)$ while $E_\\mathrm{Si}>E_\\mathrm{bd}$',fontsize=5.2,color=INK)
title(0.665,0.455,'f','Explain: design rules')
fig.savefig('/mnt/user-data/outputs/Fig1_AI-GeSPAD.pdf'); fig.savefig('/tmp/claude-0/fig/Fig1.png',dpi=300)
