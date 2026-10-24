#!/usr/bin/env python3
"""V0.4 exploratory geometry over real V15.3/U6 outputs.

Canonical engine and 244 pattern catalog are read-only. P/A/C are treated as three
abstract score coordinates for each pattern, NOT as physical coordinates or as pre-existing
recursive levels. A derived hierarchy is learned from the time-mean PAC points and clearly
labelled inferred. The module checks the native R732 against serialized boards and reports
geometric/helix diagnostics without allowing them to change H1/H2.
"""
from __future__ import annotations
import json, hashlib, math
from pathlib import Path
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist

VERSION = 'teseracto_recursivo_geometria_v0_4'
CHANNELS = ('P','A','C')
LEVEL_COUNTS = (244,122,61,31,16,8,4,2,1)
MIN_HELIX_CUTS = 5


def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()


def load_result(path):
    data=json.loads(Path(path).read_text(encoding='utf-8'))
    cuts=(data.get('motor') or {}).get('cuts')
    if not isinstance(cuts,list) or len(cuts)<2: raise ValueError('motor.cuts requiere al menos dos cortes')
    names=list((cuts[0].get('P_FULL_244') or {}).keys())
    if len(names)!=244: raise ValueError(f'P_FULL_244 requiere 244 patrones; observado={len(names)}')
    coords=np.empty((len(cuts),244,3),float)
    for t,c in enumerate(cuts):
        for j,axis in enumerate(CHANNELS):
            b=c.get(f'{axis}_FULL_244')
            if not isinstance(b,dict) or set(b)!=set(names): raise ValueError(f'{axis}_FULL_244 inconsistente en corte {t}')
            vals=np.array([b[n] for n in names],float)
            if not np.isfinite(vals).all(): raise ValueError(f'Valores no finitos en {axis}, corte {t}')
            coords[t,:,j]=vals
    return data,cuts,names,coords


def audit_r732(data,coords):
    X=coords.transpose(0,2,1).reshape(len(coords),732)
    d=np.linalg.norm(np.diff(X,axis=0),axis=1)
    r732=np.asarray((data.get('motor',{}).get('R732') or {}).get('dX_norm',[]),float)
    if len(r732)!=len(d): return {'status':'NOT_COMPARABLE','n_internal':int(len(r732)),'n_reconstructed':int(len(d)),'reconstructed':d.tolist(),'internal':r732.tolist()}
    diff=np.abs(r732-d); bound=math.sqrt(732)*1e-4
    return {'status':'PASS_EXACT_OR_ROUNDING_BOUND' if np.max(diff,initial=0)<=bound else 'FAIL_SERIALIZATION_MISMATCH',
            'internal_dX_norm':r732.tolist(),'reconstructed_dX_norm':d.tolist(),'absolute_difference':diff.tolist(),
            'max_abs_difference':float(np.max(diff,initial=0)),'rounding_bound_4dp':bound,
            'source_note':'R732 and P/A/C boards now come from the same native board instances if emission_adapter.used=false.'}


def trajectory_summary(coords,names):
    # one path per pattern in abstract PAC score-space
    T,N,_=coords.shape; out=[]
    for i,n in enumerate(names):
        p=coords[:,i,:]
        steps=np.linalg.norm(np.diff(p,axis=0),axis=1)
        out.append({'pattern':n,'step_distances':steps.tolist(),'path_length':float(steps.sum()),
                    'net_displacement':float(np.linalg.norm(p[-1]-p[0])),
                    'endpoint_contraction':bool(np.linalg.norm(p[-1]-p[0]) < np.linalg.norm(p[1]-p[0])) if T>2 else False})
    return out


def fit_helix_diagnostic(points):
    # Descriptive helix fit in abstract PAC space. Estimate axis from linear drift,
    # then project onto its perpendicular plane. >=5 cuts required; not physical validation.
    P=np.asarray(points,float); n=len(P)
    if n<MIN_HELIX_CUTS: return {'status':'INSUFFICIENT_CUTS','n_cuts':n,'minimum_required':MIN_HELIX_CUTS}
    tt=np.arange(n,dtype=float); center=P.mean(axis=0)
    # Axis estimate: endpoint drift; phase residual is later exposed by fit diagnostics.
    drift=P[-1]-P[0]
    dn=float(np.linalg.norm(drift))
    if dn<1e-10:
        return {'status':'NO_RESOLVABLE_AXIAL_DRIFT','n_cuts':n,'coordinate_interpretation':'abstract P/A/C score space'}
    axis=drift/dn
    # Stable orthonormal basis perpendicular to axis.
    ref=np.array([1.,0.,0.]) if abs(axis[0])<0.8 else np.array([0.,1.,0.])
    u=np.cross(axis,ref); u=u/(np.linalg.norm(u)+1e-15); v=np.cross(axis,u)
    centered=P-center; axial=centered@axis; x=centered@u; y=centered@v
    M=np.column_stack([x,y,np.ones(n)])
    try:
        D,E,F=np.linalg.lstsq(M,-(x*x+y*y),rcond=None)[0]
        rad2=(D*D+E*E)/4-F
        if rad2<=0: raise ValueError('nonpositive radius')
        cx,cy=-D/2,-E/2; radius=float(np.sqrt(rad2))
        radial=np.sqrt((x-cx)**2+(y-cy)**2)
        radial_cv=float(np.std(radial)/(np.mean(radial)+1e-12))
        phase=np.unwrap(np.arctan2(y-cy,x-cx))
        phase_fit=np.polyfit(tt,phase,1); phase_pred=np.polyval(phase_fit,tt)
        phase_r2=float(1-np.sum((phase-phase_pred)**2)/(np.sum((phase-phase.mean())**2)+1e-12))
        axial_fit=np.polyfit(phase,axial,1); axial_pred=np.polyval(axial_fit,phase)
        pitch_r2=float(1-np.sum((axial-axial_pred)**2)/(np.sum((axial-axial.mean())**2)+1e-12))
        return {'status':'DESCRIPTIVE_FIT_ONLY','n_cuts':n,'radius':radius,'radial_cv':radial_cv,
                'axis_unit_vector_estimate':axis.tolist(),'axial_drift_per_cut':dn,
                'phase_step_slope_rad_per_cut':float(phase_fit[0]),'phase_linearity_r2':phase_r2,
                'axial_pitch_per_radian':float(axial_fit[0]),'axial_pitch_r2':pitch_r2,
                'criteria_for_followup_not_decision':{'radial_cv_small_is_better':True,'phase_linearity_r2_near_1_is_better':True,'axial_pitch_r2_near_1_is_better':True},
                'coordinate_interpretation':'abstract P/A/C score space; not physical 3D coordinates'}
    except Exception as e:
        return {'status':'FIT_FAILED','n_cuts':n,'reason':str(e),'coordinate_interpretation':'abstract P/A/C score space'}


def derived_hierarchy(coords,names):
    # A stable, data-derived hierarchy from pooled mean PAC coordinates. This is not an asserted
    # native ontology. Linkage is fixed across cuts so cluster identities remain comparable.
    mean_pts=coords.mean(axis=0)
    Z=linkage(mean_pts,method='ward',metric='euclidean')
    levels=[]
    for k in LEVEL_COUNTS:
        labels=fcluster(Z,t=k,criterion='maxclust')
        unique=sorted(set(int(x) for x in labels))
        # centroids for each cluster at each cut
        centers=np.zeros((len(coords),len(unique),3)); cluster_sizes=[]
        for ci,lab in enumerate(unique):
            ix=np.where(labels==lab)[0]; cluster_sizes.append(int(len(ix)))
            centers[:,ci,:]=coords[:,ix,:].mean(axis=1)
        # At this resolution, calculate centroid spread within the next-coarser parent partition
        # by matching clusters to coarser labels. The coarser membership is inferred from linkage.
        spread_by_cut=[]
        # mean within-cluster spread of pattern points; robust direct diagnostic at this level
        for t in range(len(coords)):
            ds=[]
            for lab in unique:
                ix=np.where(labels==lab)[0]
                if len(ix)>1:
                    c=coords[t,ix,:].mean(axis=0)
                    ds.extend(np.linalg.norm(coords[t,ix,:]-c,axis=1).tolist())
            spread_by_cut.append(float(np.mean(ds)) if ds else 0.0)
        levels.append({'requested_clusters':k,'actual_clusters':len(unique),'cluster_size_min':min(cluster_sizes),
                       'cluster_size_max':max(cluster_sizes),'within_cluster_spread_by_cut':spread_by_cut,
                       'first_to_last_spread_change':float(spread_by_cut[-1]-spread_by_cut[0]),
                       'spread_contracts_endpoint':bool(spread_by_cut[-1]<spread_by_cut[0]),
                       'hierarchy_source':'Ward linkage over time-mean PAC points; exploratory inferred hierarchy'})
    return {'status':'DERIVED_HIERARCHY_COMPUTED_NOT_NATIVE_LEVELS','n_patterns':len(names),'levels':levels,
            'warning':'This hierarchy is inferred from geometry and does not prove the user’s hypothesized ontological recursion.'}



def helix_null_control(coords,names,n_perm=100,seed=20261020):
    """Time-order permutation control; preserves each pattern's PAC point cloud."""
    if len(coords)<MIN_HELIX_CUTS:
        return {'status':'INSUFFICIENT_CUTS','n_cuts':len(coords),'n_perm':n_perm}
    rng=np.random.default_rng(seed)
    def qualifies(h):
        return (h.get('status')=='DESCRIPTIVE_FIT_ONLY' and h.get('radial_cv',1.0)<=0.15
                and h.get('phase_linearity_r2',-1.0)>=0.90 and h.get('axial_pitch_r2',-1.0)>=0.90
                and 0.05<=abs(h.get('phase_step_slope_rad_per_cut',0.0))<=np.pi)
    real=[fit_helix_diagnostic(coords[:,i,:]) for i in range(len(names))]
    real_n=sum(qualifies(h) for h in real)
    null_counts=[]
    for _ in range(n_perm):
        n=0
        for i in range(len(names)):
            perm=rng.permutation(len(coords))
            n += int(qualifies(fit_helix_diagnostic(coords[perm,i,:])))
        null_counts.append(n)
    arr=np.asarray(null_counts,float); mean=float(arr.mean()); sd=float(arr.std())
    p=(1+int(np.sum(arr>=real_n)))/(n_perm+1)
    return {'status':'COMPUTED_EXPLORATORY','criteria':{'radial_cv_max':0.15,'phase_linearity_r2_min':0.90,'axial_pitch_r2_min':0.90,'abs_phase_slope_rad_per_cut_min':0.05},
            'n_perm':n_perm,'seed':seed,'n_real_helix_like_patterns':int(real_n),'n_patterns':len(names),
            'null_mean':mean,'null_std':sd,'null_min':int(arr.min()),'null_max':int(arr.max()),
            'z_score':float((real_n-mean)/sd) if sd>0 else 'UNDEFINED_ZERO_NULL_VARIANCE','empirical_p_one_sided':float(p),
            'interpretation':'Exploratory only; threshold is operational, small cut counts limit power, PAC coordinates are abstract scores not physical coordinates.'}


def run(path):
    data,cuts,names,coords=load_result(path)
    r_audit=audit_r732(data,coords)
    # pairwise pattern closeness per cut, with threshold sensitivity; not called convergence unless distance contracts over time
    pair_rows=[]; T,N,_=coords.shape
    for i in range(N):
        for j in range(i+1,N):
            ds=np.linalg.norm(coords[:,i,:]-coords[:,j,:],axis=1)
            pair_rows.append((i,j,ds))
    contraction=[{'patterns':[names[i],names[j]],'distances_by_cut':ds.tolist(),'endpoint_contraction':bool(ds[-1]<ds[0]),
                  'monotone_contraction':bool(np.all(np.diff(ds)<=1e-12))} for i,j,ds in pair_rows if ds[-1]<ds[0]]
    threshold_sensitivity=[]
    for tau in (0.05,0.10,0.20):
        per_cut=[]
        for t in range(T):
            per_cut.append(sum(float(np.linalg.norm(coords[t,i]-coords[t,j]))<=tau for i in range(N) for j in range(i+1,N)))
        threshold_sensitivity.append({'tau':tau,'close_pairs_by_cut':per_cut,'threshold_is_diagnostic_not_calibrated':True})
    helix=[]
    for i,n in enumerate(names):
        h=fit_helix_diagnostic(coords[:,i,:])
        if h.get('status')!='INSUFFICIENT_CUTS': helix.append({'pattern':n,**h})
    cuts_info=[c.get('corte',c.get('id',f'C{i+1}')) for i,c in enumerate(cuts)]
    return {'schema':'TESERACTO_RECURSIVO_GEOMETRIA_V0_4','version':VERSION,'source_file':Path(path).name,'source_sha256':sha256(Path(path)),
            'case_id':data.get('case_id'),'engine_version':data.get('version'),'cut_ids':cuts_info,'n_cuts':T,
            'native_integrity':{'engine_sha256':data.get('estandar',{}).get('engine_sha256'),'patterns_sha256':data.get('patterns_sha256') or data.get('estandar',{}).get('patterns_sha256'),
                               'canonical_engine_modified':False,'canonical_patterns_modified':False},
            'R732_serialization_audit':r_audit,'PAC_pattern_trajectories':{'coordinate_space':'abstract score space [P_i,A_i,C_i] per pattern i; not physical coordinates',
                'n_patterns':N,'mean_path_length':float(np.mean([x['path_length'] for x in trajectory_summary(coords,names)])),
                'mean_net_displacement':float(np.mean([x['net_displacement'] for x in trajectory_summary(coords,names)])),
                'n_pair_trajectories_with_endpoint_contraction':len(contraction),'n_pair_trajectories_monotone_contraction':sum(x['monotone_contraction'] for x in contraction),
                'examples_endpoint_contraction':contraction[:20],'threshold_sensitivity':threshold_sensitivity},
            'recursive_hierarchy':derived_hierarchy(coords,names),
            'helical_trace':{'status':'INSUFFICIENT_CUTS_FOR_HELIX_TEST' if T<MIN_HELIX_CUTS else 'DESCRIPTIVE_PAC_HELIX_FITS_COMPUTED',
                'minimum_cuts':MIN_HELIX_CUTS,'fits':helix,'time_order_null_control':helix_null_control(coords,names),
                'not_physical_validation':True},
            'billar_circular_sidecar':'Run separately; not a replacement for geometric convergence. Its v0.2 result is included in the bundle.',
            'execution_controls':{'feeds_H':False,'changes_H1_H2':False,'canonical_engine_modified':False,'canonical_patterns_modified':False}}

if __name__=='__main__':
    import sys
    out=run(sys.argv[1]); dest=Path(sys.argv[2]) if len(sys.argv)>2 else Path(sys.argv[1]).with_name('RESULT_TESERACTO_GEOMETRIA_V04.json')
    dest.write_text(json.dumps(out,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({'ok':True,'case_id':out['case_id'],'n_cuts':out['n_cuts'],'R732':out['R732_serialization_audit']['status'],
                      'hierarchy':out['recursive_hierarchy']['status'],'helix':out['helical_trace']['status'],'out':str(dest)},ensure_ascii=False))
