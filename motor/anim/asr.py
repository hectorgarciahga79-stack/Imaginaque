import sys, re, unicodedata
from faster_whisper import WhisperModel
_m=None
def model():
    global _m
    if _m is None: _m=WhisperModel("small", device="cpu", compute_type="int8")
    return _m
def norm(s):
    s=unicodedata.normalize('NFD',s.lower()); s=''.join(ch for ch in s if unicodedata.category(ch)!='Mn')
    return re.sub(r"[^a-z0-9ñ ]"," ",s).split()
def wer(ref, hyp):
    r,h=norm(ref),norm(hyp); d=list(range(len(h)+1))
    for i in range(1,len(r)+1):
        p=d[:]; d[0]=i
        for j in range(1,len(h)+1): d[j]=min(p[j]+1,d[j-1]+1,p[j-1]+(r[i-1]!=h[j-1]))
    return d[len(h)]/max(1,len(r))
def transcribe(path):
    import librosa
    audio,_=librosa.load(path, sr=16000)
    segs,_=model().transcribe(audio, language="es", word_timestamps=True, beam_size=5)
    words=[]; text=[]
    for s in segs:
        text.append(s.text)
        for w in s.words: words.append((w.word.strip(), w.start, w.end))
    return " ".join(text).strip(), words
if __name__=="__main__":
    ref=sys.argv[1]
    for p in sys.argv[2:]:
        t,_=transcribe(p); print(p.split('/')[-1], round(wer(ref,t),3), '|', t)
