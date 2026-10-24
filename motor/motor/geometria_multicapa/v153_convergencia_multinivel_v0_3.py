#!/usr/bin/env python3
"""v0_3 (corregido sobre v0_2 de ChatGPT/Mj; ver CAMBIOS al final). Auditoría geométrica de niveles recursivos, trazas helicoidales y convergencia.

Sidecar experimental; no modifica el motor canónico ni el catálogo de patrones.
Todos los mapas entre niveles deben declararse o estimarse con separación train/test.
No convierte métricas geométricas en afirmaciones físicas sin unidades y datos externos.
"""
from __future__ import annotations
import math
from typing import Any, Sequence
import numpy as np
EPS=1e-12

def trajectory(x: Any, name='trajectory') -> np.ndarray:
    a=np.asarray(x,dtype=float)
    if a.ndim!=2 or a.shape[0]<3 or a.shape[1]<1: raise ValueError(f'{name}: expected [T>=3,D>=1], got {a.shape}')
    if not np.isfinite(a).all(): raise ValueError(f'{name}: NaN/Inf input')
    return a

def compare_trajectories(a: Any,b: Any,projection_dims: Sequence[int]|None=None,tol=1e-9)->dict:
    A=trajectory(a,'A'); B=trajectory(b,'B')
    if A.shape!=B.shape: raise ValueError(f'A/B grids differ: {A.shape} vs {B.shape}; synchronize explicitly')
    d=np.linalg.norm(A-B,axis=1); dd=np.diff(d)
    ratios=[float(d[i+1]/d[i]) for i in range(len(d)-1) if d[i]>tol]
    proj=None
    if projection_dims is not None:
        idx=np.asarray(projection_dims,dtype=int)
        if idx.ndim!=1 or len(idx)<1 or np.any(idx<0) or np.any(idx>=A.shape[1]): raise ValueError('invalid projection_dims')
        dp=np.linalg.norm(A[:,idx]-B[:,idx],axis=1)
        proj={'minimum_projected_distance':float(dp.min()),'minimum_full_space_distance':float(d.min()),
              'projection_intersection':bool(dp.min()<=tol),'full_space_intersection':bool(d.min()<=tol),
              'projection_false_positive':bool(dp.min()<=tol and d.min()>tol),
              'projected_distance_sequence':dp.tolist(),
              'per_cut_projection_false_positive':[bool(p<=tol and q>tol) for p,q in zip(dp,d)]}
    return {'n_cuts':len(d),'dimension':A.shape[1],'initial_distance':float(d[0]),'final_distance':float(d[-1]),
      'minimum_distance':float(d.min()),'distance_sequence':d.tolist(),'monotone_nonincreasing':bool(np.all(dd<=tol)),
      'observed_endpoint_convergence':bool(d[-1]<=tol),'max_defined_step_ratio':max(ratios) if ratios else None,
      'contraction_each_defined_step':bool(len(ratios)==len(d)-1 and all(r<1 for r in ratios)),
      'projection_test':proj,'tolerance':float(tol),
      'final_over_initial':float(d[-1]/d[0]) if d[0]>tol else None}

def apply_affine_map(child: Any,matrix: Any,offset: Any)->np.ndarray:
    X=trajectory(child,'child level'); M=np.asarray(matrix,dtype=float); b=np.asarray(offset,dtype=float)
    if M.ndim!=2 or M.shape[1]!=X.shape[1] or b.shape!=(M.shape[0],): raise ValueError('affine map shape mismatch')
    if not np.isfinite(M).all() or not np.isfinite(b).all(): raise ValueError('nonfinite map')
    return X@M.T+b

def fit_affine_map_holdout(child: Any,parent: Any,train_fraction=.7)->dict:
    """Fit child->parent affine map on early cuts; report held-out residual on later cuts."""
    X=trajectory(child,'child'); Y=trajectory(parent,'parent')
    if len(X)!=len(Y): raise ValueError('child/parent must be temporally synchronized')
    if not 0.5<=train_fraction<1: raise ValueError('train_fraction must be in [0.5,1)')
    n=max(X.shape[1]+2,int(math.floor(len(X)*train_fraction)))
    if n>=len(X): raise ValueError('insufficient held-out cuts for dimension and split')
    D=np.c_[X[:n],np.ones(n)]
    coef,_,rank,_=np.linalg.lstsq(D,Y[:n],rcond=None)
    pred=np.c_[X[n:],np.ones(len(X)-n)]@coef
    err=np.linalg.norm(pred-Y[n:],axis=1)
    baseline=np.linalg.norm(Y[n:]-Y[:n].mean(axis=0),axis=1)
    return {'train_cuts':n,'test_cuts':len(X)-n,'design_rank':int(rank),'design_columns':int(D.shape[1]),
      'map_identifiable_on_train':bool(rank==D.shape[1]),'test_residual_mean':float(err.mean()),'test_residual_max':float(err.max()),
      'test_parent_scale_mean':float(baseline.mean()),'normalized_test_residual':float(err.mean()/(baseline.mean()+EPS)),
      'affine_matrix':coef[:-1].T.tolist(),'affine_offset':coef[-1].tolist(),
      'warning':'A low holdout residual supports predictability of this mapping, not causal or physical validity.'}

def recursive_hierarchy(levels: Sequence[Any],maps: Sequence[dict]|None=None,tol=1e-9)->dict:
    """Compare each child mapped into its parent's coordinates. maps[i]={matrix,offset}."""
    if len(levels)<2: raise ValueError('need at least two levels')
    arr=[trajectory(v,f'level[{i}]') for i,v in enumerate(levels)]
    if any(len(x)!=len(arr[0]) for x in arr): raise ValueError('levels must share synchronized cuts')
    if maps is not None and len(maps)!=len(arr)-1: raise ValueError('one map required per adjacent level pair')
    residuals=[]; mapped=[]
    for i in range(len(arr)-1):
        child=arr[i]
        if maps is not None: child=apply_affine_map(child,maps[i]['matrix'],maps[i]['offset'])
        if child.shape!=arr[i+1].shape: raise ValueError(f'mapped level {i} shape {child.shape} != parent {arr[i+1].shape}')
        r=np.linalg.norm(child-arr[i+1],axis=1); residuals.append(r); mapped.append(child)
    means=[float(r.mean()) for r in residuals]
    ratios=[means[i+1]/means[i] for i in range(len(means)-1) if means[i]>tol]
    return {'levels':len(arr),'cuts':len(arr[0]),'adjacent_residual_mean':means,
      'adjacent_residual_max':[float(r.max()) for r in residuals],
      'residual_nonincreasing_by_level':bool(all(means[i+1]<=means[i]+tol for i in range(len(means)-1))),
      'residual_contraction_ratios':ratios,'strict_contraction_all_defined':bool(len(ratios)==len(means)-1 and all(r<1 for r in ratios)),
      'all_adjacent_equal_within_tolerance':bool(all(r.max()<=tol for r in residuals)),
      'maps_explicitly_supplied':maps is not None,'interpretation':'Recursive geometric consistency in mapped coordinates; not physical validation.'}

def helix_diagnostics(x: Any,axis: Any=None,eps=EPS)->dict:
    """Fit a descriptive 3-D helix frame using PCA; report radius/phase/axial diagnostics.

    A fit is labelled helix-like only when phase advances consistently and radius is stable.
    PCA axis sign is arbitrary; reported pitch is therefore signed only relative to that axis.
    """
    X=trajectory(x,'helix')
    n_pts=len(X)
    if X.shape[1]!=3: raise ValueError('helix_diagnostics requires exactly 3 coordinates')
    center=X.mean(axis=0); Y=X-center
    axis_source='pca_estimate'
    if axis is None:
        _,s,Vt=np.linalg.svd(Y,full_matrices=False); axis=Vt[0]
    else:
        axis=np.asarray(axis,dtype=float)
        if axis.shape!=(3,) or not np.isfinite(axis).all() or np.linalg.norm(axis)<=eps: raise ValueError('axis must be a finite nonzero 3-vector')
        axis=axis/np.linalg.norm(axis); axis_source='provided_axis'
    axial=Y@axis; radial=Y-np.outer(axial,axis); radius=np.linalg.norm(radial,axis=1)
    # Build orthonormal radial basis from first nonzero radial sample.
    norms=np.linalg.norm(radial,axis=1); valid=np.where(norms>eps)[0]
    if len(valid)<3: return {'helix_like':False,'reason':'insufficient radial variation','axis':axis.tolist(),'axis_source':axis_source}
    e1=radial[valid[0]]/norms[valid[0]]; e2=np.cross(axis,e1); e2=e2/(np.linalg.norm(e2)+eps)
    xx=radial@e1; yy=radial@e2; phase=np.unwrap(np.arctan2(yy,xx)); dphi=np.diff(phase); da=np.diff(axial)
    active=np.abs(dphi)>eps; slopes=da[active]/dphi[active] if np.any(active) else np.array([])
    rmean=float(radius.mean()); rcv=float(radius.std()/(rmean+eps));
    sign_consistency=float(max(np.mean(dphi>=0),np.mean(dphi<=0)))
    pitch=float(2*np.pi*np.median(slopes)) if len(slopes) else None
    return {'helix_like':bool(rcv<0.15 and sign_consistency>0.9 and np.count_nonzero(active)>=max(2,int(.5*len(dphi)))),
      'axis':axis.tolist(),'axis_source':axis_source,'center':center.tolist(),'radius_mean':rmean,'radius_cv':rcv,
      'phase_total_turns':float((phase[-1]-phase[0])/(2*np.pi)),'phase_direction_consistency':sign_consistency,
      'axial_displacement':float(axial[-1]-axial[0]),'pitch_per_turn_median':pitch,
      'phase_increment_median_abs':float(np.median(np.abs(dphi))),
      'n_points':int(n_pts),'low_n_warning':bool(n_pts<20),
      'warning':'Descriptive fit only; axis and pitch depend on sampled interval and coordinate scaling. With few points (<20) phase unwrap is ambiguous and a PCA axis tends to align with the overall drift, biasing toward a spurious axial component.'}

def finite_diagnostics(x: Any,eps=EPS)->dict:
    X=trajectory(x); V=np.diff(X,axis=0); speed=np.linalg.norm(V,axis=1); persistence=[]
    for a,b in zip(V[:-1],V[1:]):
        den=np.linalg.norm(a)*np.linalg.norm(b); persistence.append(float(np.dot(a,b)/den) if den>eps else None)
    dp=np.diff(X,axis=0); centered=dp-dp.mean(axis=0,keepdims=True); cov=centered.T@centered
    den=np.sqrt(np.maximum(np.diag(cov),0)); valid=(den[:,None]>eps)&(den[None,:]>eps); corr=np.zeros_like(cov)
    np.divide(cov,den[:,None]*den[None,:],out=corr,where=valid); corr=np.clip(corr,-1,1)
    return {'n_cuts':len(X),'dimension':X.shape[1],'speed':speed.tolist(),'zero_velocity_count':int(np.count_nonzero(speed<=eps)),
      'persistence_cosine':persistence,'undefined_persistence_count':sum(v is None for v in persistence),
      'delta_correlation':corr.tolist(),'correlation_valid_mask':valid.tolist(),
      'undefined_correlation_count':int(valid.size-np.count_nonzero(valid)),
      'all_numeric_outputs_finite':bool(np.isfinite(speed).all() and np.isfinite(corr).all())}

def tusi_local_coupling(a: Any,b: Any,eps=EPS)->dict:
    a=np.asarray(a,float); b=np.asarray(b,float)
    if a.shape!=b.shape or a.ndim!=1 or not np.isfinite(a).all() or not np.isfinite(b).all(): raise ValueError('increments must be finite equal-length 1D arrays')
    den=np.abs(a)+np.abs(b); vals=[None if z<=eps else float(np.clip(1-abs(u+v)/z,0,1)) for u,v,z in zip(a,b,den)]
    good=[v for v in vals if v is not None]
    return {'local_indices':vals,'mean_local_index':float(np.mean(good)) if good else None,'valid_steps':len(good),'undefined_steps':len(vals)-len(good)}


def tusi_aggregate_motor(a: Any,b: Any)->dict:
    """Fórmula del motor (tusi_par_indice_exploratorio_v0_1 / puente_souriau._tusi): 1-|Σ(a+b)|/Σ(|a|+|b|),
    sólo pasos con ambos definidos y no ambos cero; None si <2 pasos. Se recomienda usar la del motor directamente."""
    pares=[(float(x),float(y)) for x,y in zip(a,b) if x is not None and y is not None and (x!=0 or y!=0)]
    if len(pares)<2: return {'tusi':None,'n_pasos_vivos':len(pares)}
    num=abs(sum(x+y for x,y in pares)); den=sum(abs(x)+abs(y) for x,y in pares)
    return {'tusi':(1-num/den) if den else None,'n_pasos_vivos':len(pares)}

CAMBIOS_V0_3 = [
  "helix_diagnostics: añade n_points y low_n_warning (<20 puntos); advertencia de sesgo del eje PCA.",
  "compare_trajectories: projection_test añade projected_distance_sequence y per_cut_projection_false_positive; añade final_over_initial. tol debe fijarse en la escala de los datos (con datos reales 1e-9 no tiene sentido).",
  "tusi_local_coupling se conserva pero NO es la fórmula del motor: es la media de índices locales por paso; la del motor es agregada (tusi_aggregate_motor). Difieren en general.",
  "Test reescrito para pytest (tests/test_convergencia_v0_3.py), sin carpeta 'extracted', hash reproducible con redondeo a 10 decimales.",
]
