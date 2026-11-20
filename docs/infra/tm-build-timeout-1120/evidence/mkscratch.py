import os, shutil, sys
src, dst = sys.argv[1], sys.argv[2]
shutil.copytree(src, dst, symlinks=True, ignore=shutil.ignore_patterns('.lake', '.cache'))
shutil.copytree(os.path.join(src, '.lake'), os.path.join(dst, '.lake'), symlinks=True,
                copy_function=lambda s, d: os.link(s, d) if s.endswith('.olean') else shutil.copy2(s, d))
p = os.path.join(dst, 'VE/Compose/Dispatch.lean')
open(p, 'a').write('\n/-- tmbto measurement probe: a new declaration, so the module and its whole cone rebuild. -/\ndef tmbtoConeProbe : Nat := 0\n')
