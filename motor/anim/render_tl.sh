cd /home/claude/anim
for v in "$@"; do
python3 -c "
import pipeline, scenes, json
v='$v'; tl=json.load(open(f'build/{v}/timeline.json')); pipeline.build_ass(v, tl); pipeline.render_frames(v, tl, scenes); pipeline.mux(v, tl, scenes.BOOMS.get(v, ()))
print('RENDERED', v, round(tl['total'],1), flush=True)" 2>&1 | grep -E "RENDERED|Error|Traceback"
done
