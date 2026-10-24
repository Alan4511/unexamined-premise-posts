from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import textwrap

OUT=Path("posts/001-personal-journey")
OUT.mkdir(parents=True,exist_ok=True)
BG="#F3F0E9"; INK="#282822"; MUTED="#77736D"; RUST="#AD715C"
SERIF="/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SLIDES=[["THE QUESTION","I started with\\na statistic.","I wondered when a statistical difference becomes a reliable trend, and when a trend allows us to claim causality.\\n\\nIn particular: if women are promoted less often than men, how do we know discrimination is the cause?\\n\\nI wasn't denying that discrimination exists. I was questioning the inference that takes us from a measured difference to a particular explanation."],["A DOUBT","Would I interpret\\nevery gap the same?","I imagined running the same analysis across race, age, and education. What if it showed a disadvantage for a group we don't usually think of as historically oppressed?\\n\\nWould I demand more evidence in that case?\\n\\nI began to suspect that historical narratives might shape which statistical explanations we accept. But history is relevant evidence too. How much weight should I give it?"],["WHAT THE DATA CAN SAY","I realised that\\nprecision isn't causality.","A larger sample can make me increasingly confident that a difference is real. It can't, by itself, tell me why the difference exists.\\n\\nI learned to distinguish a reliable statistical association from a causal explanation.\\n\\nEven when a gap remains after statistical controls, unmeasured influences may remain. Conversely, some controls may conceal a discriminatory pathway. I had underestimated that complication."],["THE QUESTION SHIFTS","Then I wondered\\nwhat counts as unfair.","Suppose one employee continues working while another takes time away to raise a child. If the first gains experience and earns a promotion, I struggle to call that inherently unjust.\\n\\nI believe society can support parents without requiring employers to grant identical professional trajectories.\\n\\nYet the next question unsettled me: how freely did the parent choose to step away?"],["CHOICE OR CONDITIONING","I couldn't ignore\\nsocial expectations.","Women have historically been expected to carry more domestic responsibility. Those expectations may still influence choices about who stays home.\\n\\nI could acknowledge this without assuming every homemaker had been coerced.\\n\\nBut how can we separate a genuine personal preference from a preference gradually formed by the society someone grew up in?"],["MY OWN OBJECTION","Then I questioned\\nthe question itself.","Every preference I have is shaped by some social history. A person who admires traditional family life and one who prizes professional independence have both learned values from the world around them.\\n\\nWhy should I assume only one of those preferences is conditioned?\\n\\nAnd at what point does something I learned to want become something I truly want?"],["AN UNCOMFORTABLE LIMIT","I was tempted to say:\\nlet happiness decide.","If a woman is fulfilled by homemaking, who am I—or any reformer—to declare her choice illegitimate?\\n\\nBut then I had to challenge myself. People can sincerely adapt to restricted possibilities. Happiness doesn't prove that meaningful alternatives existed.\\n\\nAt the same time, calling someone's contentment false merely because of its history seems paternalistic."],["NIETZSCHE ENTERS","Nietzsche made me\\nless certain.","His criticism of inherited morality helped me ask whether the traditionalist and the reformer might both be repeating values handed to them.\\n\\nYet Nietzsche also troubled my reliance on happiness: comfort and satisfaction don't necessarily amount to self-mastery.\\n\\nI couldn't simply recruit him to validate my position. His questions also turned against my own assumptions."],["A POSSIBLE DIRECTION","I began thinking\\nabout alternatives.","Perhaps the more useful question is whether a person has meaningful opportunities to live differently, can question their inherited expectations, and still endorses their choice.\\n\\nThat seems less intrusive than judging whether their preference has a pure origin.\\n\\nBut even the ability to reflect is socially shaped. I still don't know exactly where freedom begins."],["STILL UNFINISHED","I started with causality.\\nI ended with free will.","I haven't resolved how to respect individuals' chosen lives while taking structural pressures seriously. Nor have I settled when an unequal outcome becomes an injustice that society should correct.\\n\\nWhat changed was the question itself.\\n\\nThis is not a conclusion about how others ought to live. It's a record of why I'm less confident in the explanations I once found straightforward."]]

def draw_text(d,xy,text,font,fill,max_width,spacing=17):
    x,y=xy
    for para in text.split("\n"):
        if not para:
            y+=font.size//2
            continue
        words=para.split(); line=""
        for word in words:
            candidate=(line+" "+word).strip()
            if d.textbbox((0,0),candidate,font=font)[2]>max_width and line:
                d.text((x,y),line,font=font,fill=fill); y+=font.size+spacing;line=word
            else: line=candidate
        if line:
            d.text((x,y),line,font=font,fill=fill);y+=font.size+spacing
    return y

for index,(tag,heading,body) in enumerate(SLIDES,1):
    # Decode escaped line breaks in JSON-authored slide text before layout.
    heading=heading.replace(chr(92)+'n',chr(10))
    body=body.replace(chr(92)+'n',chr(10))
    img=Image.new("RGB",(1080,1350),BG); d=ImageDraw.Draw(img)
    small=ImageFont.truetype(SANS,19)
    tagfont=ImageFont.truetype(BOLD,20)
    headfont=ImageFont.truetype(SERIF,49 if index!=1 else 65)
    bodyfont=ImageFont.truetype(SANS,29 if index!=1 else 30)
    foot=ImageFont.truetype(SANS,16)
    d.text((80,78),"THE UNEXAMINED PREMISE",font=small,fill=RUST)
    d.text((938,78),f"{index:02d}/10",font=small,fill=MUTED)
    d.line((80,119,1000,119),fill="#D8D4CB",width=2)
    d.text((80,205),tag,font=tagfont,fill=RUST)
    hy=280
    for part in heading.split("\n"):
        d.text((80,hy),part,font=headfont,fill=INK);hy+=headfont.size+23
    hy+=34
    draw_text(d,(80,hy),body,bodyfont,MUTED,895,16)
    d.line((80,1260,1000,1260),fill="#D8D4CB",width=2)
    d.text((80,1280),"UNFINISHED ARGUMENT 001",font=foot,fill=MUTED)
    img.save(OUT/f"{index:02d}.png",optimize=True)
print(f"Generated {len(SLIDES)} images in {OUT}")
