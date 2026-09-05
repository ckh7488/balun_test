"""Read-only audit. Run with KiCad 10 pcbnew Python from any directory."""
import json, math, hashlib
from collections import Counter, defaultdict
from pathlib import Path
import pcbnew as p
ROOT=Path(__file__).resolve().parents[2]
BOARDS=['balun_eth_rj45/balun_eth_rj45']+[f'adapters/{n}/{n}' for n in ['m12_slipring','m12_llc','molex_slipring']]
out={}
for stem in BOARDS:
    path=ROOT/(stem+'.kicad_pcb'); b=p.LoadBoard(str(path))
    widths=defaultdict(Counter); lengths=defaultdict(float); close=[]; trunks=[]
    tracks=[t for t in b.GetTracks() if not isinstance(t,p.PCB_VIA)]
    for t in tracks:
        net=t.GetNetname(); w=round(p.ToMM(t.GetWidth()),6)
        widths[net][str(w)]+=1; lengths[net]+=p.ToMM(t.GetLength())
        if '_P' in net or '_N' in net:
            assert w in (.234,.15),(stem,net,w)
        if net.startswith('Net-(J') and net.endswith('-In)'): assert w==.357,(stem,net,w)
    # Parallel straight sections, including oblique trunks. Excludes fanout.
    for a in tracks:
        if '_P' not in a.GetNetname(): continue
        ax,ay=p.ToMM(a.GetStart().x),p.ToMM(a.GetStart().y)
        dx,dy=p.ToMM(a.GetEnd().x-a.GetStart().x),p.ToMM(a.GetEnd().y-a.GetStart().y)
        length=math.hypot(dx,dy)
        if length<5: continue
        ux,uy=dx/length,dy/length
        for c in tracks:
            if c.GetNetname()!=a.GetNetname().replace('_P','_N') or c.GetLayer()!=a.GetLayer(): continue
            cx,cy=p.ToMM(c.GetStart().x),p.ToMM(c.GetStart().y)
            ex,ey=p.ToMM(c.GetEnd().x),p.ToMM(c.GetEnd().y)
            cross=abs((ex-cx)*uy-(ey-cy)*ux)
            if cross>.00001: continue
            q1=(cx-ax)*ux+(cy-ay)*uy;q2=(ex-ax)*ux+(ey-ay)*uy
            overlap=min(length,max(q1,q2))-max(0,min(q1,q2))
            if overlap<5: continue
            pitch=abs((cx-ax)*uy-(cy-ay)*ux)
            gap=pitch-p.ToMM(a.GetWidth()+c.GetWidth())/2
            if pitch<1: trunks.append({'net':a.GetNetname(),'layer':b.GetLayerName(a.GetLayer()),'overlap_mm':round(overlap,6),'center_pitch_mm':round(pitch,6),'edge_gap_mm':round(gap,6)})
    assert trunks and all(abs(t['edge_gap_mm']-.216)<.000003 for t in trunks),(stem,trunks)
    for v in b.GetTracks():
        if not isinstance(v,p.PCB_VIA): continue
        vr=p.ToMM(v.GetWidth(p.F_Cu))/2
        for f in b.GetFootprints():
            for pad in f.Pads():
                if pad.GetAttribute()==p.PAD_ATTRIB_NPTH or not(pad.IsOnLayer(p.F_Cu) or pad.IsOnLayer(p.B_Cu)): continue
                dx=p.ToMM(v.GetPosition().x-pad.GetPosition().x);dy=p.ToMM(v.GetPosition().y-pad.GetPosition().y)
                ang=math.radians(pad.GetOrientationDegrees()); x=dx*math.cos(ang)+dy*math.sin(ang);y=-dx*math.sin(ang)+dy*math.cos(ang)
                sx=p.ToMM(pad.GetSize().x)/2;sy=p.ToMM(pad.GetSize().y)/2
                if pad.GetShape()==p.PAD_SHAPE_CIRCLE: dist=math.hypot(x,y)-sx
                elif pad.GetShape()==p.PAD_SHAPE_OVAL:
                    dist=(math.hypot(max(abs(x)-(sx-sy),0),y)-sy) if sx>=sy else (math.hypot(x,max(abs(y)-(sy-sx),0))-sx)
                else: dist=math.hypot(max(abs(x)-sx,0),max(abs(y)-sy,0))
                gap=dist-vr
                if gap<.35-1e-6: close.append({'ref':f.GetReference(),'pad':pad.GetNumber(),'via_mm':[p.ToMM(v.GetPosition().x),p.ToMM(v.GetPosition().y)],'copper_edge_gap_mm':round(gap,4)})
    out[stem]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'track_width_counts':dict(widths),'track_lengths_mm':dict(lengths),'parallel_trunks':trunks,'via_pad_gap_under_0_35_mm':close,'via_pad_audit_limit':'Copper-edge distance; rectangular bounding box for non-circle/oval pads. Confirm mask/CAM plug eligibility with manufacturer.'}
print(json.dumps(out,indent=2))
