from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import textwrap

OUT=Path("posts/001-when-does-a-choice-become-our-own")
OUT.mkdir(parents=True,exist_ok=True)
BG="#F3F0E9"; INK="#282822"; MUTED="#77736D"; RUST="#AD715C"
SERIF="/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SLIDES=[
("AN UNFINISHED INQUIRY","When does a choice\nbecome our own?","On statistics, unequal opportunities, social conditioning, and the freedom to live differently."),
("OBSERVATION / CAUSATION","A disparity is not\nan explanation.","Suppose women are promoted less often than men. That is a measurable difference. It does not, by itself, tell us why the difference exists.\n\nDiscrimination is one possible cause. Working patterns, caregiving, preferences, and workplace structures may also matter. Some of those factors may themselves be consequences of discrimination.\n\nThe statistical question is whether the gap is real. The causal question is what produces it."),
("HISTORY / EVIDENCE","What are we prepared\nto believe?","If a comparable promotion gap disadvantages men, or members of a historically dominant racial group, would we interpret it the same way?\n\nHistory should inform what we investigate. It should not determine our conclusion in advance.\n\nThe same standards of evidence ought to apply whichever group appears worse off. An unexplained gap calls for investigation; it is not automatically proof of a particular explanation."),
("INEQUALITY / INJUSTICE","When does inequality\nbecome unfair?","Imagine two parents who pause their careers to raise a child, and a third employee who continues working. The third develops more experience and receives a promotion.\n\nIf the decision reflects genuinely greater contribution, why must the outcome be corrected?\n\nSupporting parents as a society and awarding promotions at work are different questions. Equal opportunity need not entail identical career trajectories."),
("PREFERENCE / PRESSURE","But was the choice\nreally free?","Women often shoulder more of the work of caring for children. That division may reflect genuine preferences, practical constraints, or inherited expectations—usually some mixture.\n\nIf a woman chooses to become a homemaker, we can ask whether society shaped that preference.\n\nYet explaining where a preference came from does not, on its own, tell us whether she was coerced into it."),
("CONDITIONING / AUTONOMY","Every preference\nhas a history.","A person raised to admire domestic life may choose homemaking. Another raised to prize professional independence may choose a career.\n\nBoth were influenced by their surroundings. Why should the first choice be dismissed as conditioning while the second is celebrated as authentic?\n\nIf every socially formed preference is unfree, almost no human preference escapes the accusation."),
("HAPPINESS / FREEDOM","Does happiness\nsettle it?","Not entirely. People can find sincere satisfaction within restricted circumstances. Happiness does not prove that meaningful alternatives were available.\n\nBut neither may an outsider dismiss someone's happiness merely because the person's chosen life seems unfashionable.\n\nBoth mistakes deny something important: the reality of constraints, and the authority individuals have to speak for themselves."),
("FREEDOM / REFLECTION","Perhaps freedom is\nthe ability to reconsider.","Could someone pursue another life without coercion or exclusion? Do they know their alternatives? Can they question their upbringing and still choose the same path?\n\nThat seems a better test than asking whether society influenced their desires.\n\nYet even our ability to reflect is shaped by education, culture, and experience. There may be no perfectly independent vantage point."),
("REFORM / PATERNALISM","What, then, should\nreform correct?","There is a difference between widening the choices available to people and deciding which choices liberated people ought to make.\n\nWe can challenge discrimination, coercion, and closed doors without treating every unequal outcome as a failure.\n\nStill, how do we tell a genuinely chosen difference from a constraint so familiar that it no longer feels like one?"),
("AN UNFINISHED ARGUMENT","A second thought,\nnot a final answer.","I began by asking how statistics justify a causal claim. I ended up asking when a socially formed desire becomes a free choice.\n\nI remain unsure where to draw that line.\n\nPerhaps the purpose of examining our assumptions is not to escape influence altogether, but to leave ourselves open to changing our minds.")
]

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
