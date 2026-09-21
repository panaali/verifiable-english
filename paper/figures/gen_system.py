#!/usr/bin/env python3
"""Draw the committed interface schematic without a TeX dependency."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
ROOT=Path(__file__).resolve().parents[1]
plt.rcParams.update({'font.family':'DejaVu Sans','svg.hashsalt':'ve-paper-system'})
def main():
    data=json.loads((ROOT/'sources/system-diagram.json').read_text())
    fig,ax=plt.subplots(figsize=(8.4,6.1),layout='constrained')
    nodes={n['id']:n for n in data['nodes']}
    width,height=3.1,.8
    for a,b in data['arrows']:
        p,q=nodes[a],nodes[b]
        dx,dy=q['x']-p['x'],q['y']-p['y']
        if dx==0:
            s=1 if dy>0 else -1; start=(p['x'],p['y']+s*height/2);end=(q['x'],q['y']-s*height/2)
        elif dy==0:
            s=1 if dx>0 else -1; start=(p['x']+s*width/2,p['y']);end=(q['x']-s*width/2,q['y'])
        else:
            start=(p['x']-width/2,p['y']-.12);end=(q['x']+width/2,q['y']+.12)
        ax.add_patch(FancyArrowPatch(start,end,arrowstyle='-|>',mutation_scale=13,color='#455461',linewidth=1.2))
    for n in nodes.values():
        fill='#e7edf3' if n['kind']=='judgment' else 'white'
        ax.add_patch(FancyBboxPatch((n['x']-width/2,n['y']-height/2),width,height,boxstyle='round,pad=0.035',facecolor=fill,edgecolor='#455461',linestyle='--' if n['kind']=='untrusted' else '-',linewidth=1.1))
        ax.text(n['x'],n['y'],n['text'],ha='center',va='center',fontsize=9)
    ax.set(xlim=(-.1,7.5),ylim=(-.05,7.2));ax.axis('off')
    for suffix in ['pdf','svg','png']:
        meta={'Creator':'VE paper generator'}
        if suffix=='pdf':meta.update(CreationDate=None,ModDate=None)
        elif suffix=='svg':meta.update(Date=None)
        fig.savefig(ROOT/f'figures/system.{suffix}',dpi=180,metadata=meta)
    plt.close(fig)
    print('System diagram generated from committed interface data.')
if __name__=='__main__':main()
