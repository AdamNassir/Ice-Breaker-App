"""Rebuild the four social screenshots: python build_question_images.py.

Optional authoring dependency only: python -m pip install Pillow
The deployed game uses the bundled PNGs and does not need Pillow.
Edit LINKEDIN_POST, TEAMS_REQUEST, TEAMS_REPLY, PDF_LINES, or AI_TWEET below.
GENUINE_TWEET reproduces a verified public post; preserve it for HUMAN provenance.
All interface graphics are reconstructions; the other social texts are fictional.
"""
from pathlib import Path
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent / "static" / "images"
LINKEDIN_POST = (
    "This morning, I asked our AI agent to prioritize the roadmap.\n\n"
    "It deleted the backlog.\n\n"
    "At first, I called it a bug. Then I realized: our customers had never "
    "asked for a backlog. They asked for outcomes.\n\n"
    "We now have zero technical debt, zero missed deadlines, and zero features.\n\n"
    "The board calls it a shutdown. I call it radical focus.\n\n"
    "What has your AI agent taught you about leadership?\n"
    "#BuildInPublic #AgenticEverything"
)
TEAMS_REQUEST = (
    "Hi, here is the final technical document for the quarterly project wrap-up. "
    "It covers our shared spreadsheet for the office coffee rota: who refills "
    "the beans each week. Can you read it and validate before I close the project?"
)
TEAMS_REPLY = (
    "Validated. This is a strong plan for automating coffee supply across all our "
    "offices. The live inventory dashboard should predict demand, place orders "
    "with suppliers and reroute deliveries when a site runs low. I also like "
    "the access controls that stop unauthorized purchases and the backup "
    "system that keeps everything running during an outage. My only "
    "recommendation is to add a rollout plan for international offices. "
    "Otherwise, ready to launch."
)
PDF_LINES = [
    "Q3 PROJECT WRAP-UP", "Office coffee rota", "Final technical document",
    "One shared spreadsheet. Three columns:", "Name | Week | Refill beans",
    "Everyone edits their own row manually.", "Friday: check next week's volunteer.",
    "Success: no empty coffee machine.", "No servers. No API. No automation.",
]
GENUINE_TWEET = 'Has anyone noticed that, since I said "I HATE TAYLOR SWIFT," she\'s no longer "HOT?"'
GENUINE_TWEET_SOURCE = "https://truthsocial.com/@realDonaldTrump/posts/114517718765768352"
AI_TWEET = (
    "We will build the biggest FIREWALL anyone has ever seen. Beautiful firewall. "
    "And the hackers are going to pay for it. They said nobody could secure a "
    "network with CAPS LOCK. WRONG!"
)


def font(size, bold=False):
    names = ["/usr/share/fonts/opentype/urw-base35/NimbusSans-Bold.otf" if bold else
             "/usr/share/fonts/opentype/urw-base35/NimbusSans-Regular.otf",
             "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
             str(Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" /
                 ("arialbd.ttf" if bold else "arial.ttf")),
             "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else
             "/System/Library/Fonts/Supplemental/Arial.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)


def text(draw, xy, value, size=26, fill="#242424", bold=False):
    draw.text(xy, value, font=font(size, bold), fill=fill)


def paragraph(draw, xy, value, width, size=26, line=38, fill="#242424"):
    x, y = xy
    face = font(size)
    for part in value.split("\n"):
        words, current = part.split(), ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if current and draw.textlength(candidate, font=face) > width:
                draw.text((x, y), current, font=face, fill=fill)
                y += line
                current = word
            else:
                current = candidate
        draw.text((x, y), current, font=face, fill=fill)
        y += line if part else int(line * .65)
    return y


# CHANGE these block sizes for the two Trump cards. Larger blocks hide more.
SOCIAL_NAME_PIXEL_SIZE = 24
SOCIAL_AVATAR_PIXEL_SIZE = 20


def pixelate(tile, block_size):
    """Destructively average identity details, then draw solid square pixels."""
    width, height = tile.size
    reduced = tile.resize((max(1, width // block_size), max(1, height // block_size)),
                          Image.Resampling.BOX)
    return reduced.resize(tile.size, Image.Resampling.NEAREST)


def avatar(image, xy, size=88, color="#d5dfeb", blur=5, pixel_size=None):
    x, y = xy
    tile = Image.new("RGB", (size, size), color)
    d = ImageDraw.Draw(tile)
    d.ellipse((size*.30, size*.12, size*.72, size*.62), fill="#ecc4a3")
    d.ellipse((size*.29, size*.06, size*.73, size*.32), fill="#c9b28b")
    d.polygon([(size*.12,size),(size*.30,size*.58),(size*.51,size*.72),
               (size*.73,size*.58),(size*.95,size)], fill="#23354d")
    d.polygon([(size*.43,size*.65),(size*.55,size*.65),(size*.58,size),
               (size*.45,size)],fill="#bc3036")
    mask=Image.new("L",(size,size),0)
    ImageDraw.Draw(mask).ellipse((0,0,size-1,size-1),fill=255)
    hidden = pixelate(tile, pixel_size) if pixel_size else tile.filter(ImageFilter.GaussianBlur(blur))
    image.paste(hidden,(x,y),mask)


def blurred_label(image, xy, value, size=30, width=350, height=46, bold=False,
                  bg="white", fill="#161616", radius=5, pixel_size=None):
    tile=Image.new("RGB",(width,height),bg)
    text(ImageDraw.Draw(tile),(0,0),value,size,fill,bold)
    hidden = pixelate(tile, pixel_size) if pixel_size else tile.filter(ImageFilter.GaussianBlur(radius))
    image.paste(hidden,xy)


def icon(d, xy, kind, scale=1, color="#656565"):
    x,y=xy; w=max(2,round(2*scale))
    def line(points):d.line([(x+a*scale,y+b*scale) for a,b in points],fill=color,width=w)
    if kind=="comment":
        d.rounded_rectangle((x,y,x+26*scale,y+20*scale),radius=5*scale,outline=color,width=w)
        line([(6,20),(3,27),(14,20)])
    elif kind=="repost":
        line([(2,11),(2,4),(25,4),(20,0)]);line([(25,4),(20,8)])
        line([(25,15),(25,24),(2,24),(7,28)]);line([(2,24),(7,20)])
    elif kind=="send":
        line([(0,10),(28,0),(18,28),(12,16),(0,10)]);line([(12,16),(28,0)])
    elif kind=="like":
        line([(4,12),(10,12),(15,0),(20,0),(20,10),(29,10),(26,28),(10,28),(10,12)])
        d.rectangle((x,y+12*scale,x+6*scale,y+28*scale),outline=color,width=w)
    elif kind=="heart":
        d.arc((x,y,x+15*scale,y+16*scale),180,340,fill=color,width=w)
        d.arc((x+13*scale,y,x+28*scale,y+16*scale),200,360,fill=color,width=w)
        line([(0,9),(14,27),(28,9)])
    elif kind=="share":
        line([(0,14),(0,28),(26,28),(26,14)]);line([(13,22),(13,0),(5,8)])
        line([(13,0),(21,8)])
    elif kind=="calendar":
        d.rounded_rectangle((x,y+3*scale,x+26*scale,y+27*scale),3*scale,outline=color,width=w)
        line([(0,10),(26,10)]);line([(7,0),(7,6)]);line([(19,0),(19,6)])
        for a,b in [(7,16),(18,16),(7,22),(18,22)]:
            d.rectangle((x+a*scale,y+b*scale,x+(a+2)*scale,y+(b+2)*scale),fill=color)
    elif kind=="phone":
        line([(6,0),(1,3),(0,10),(4,20),(13,28),(22,31),(28,28),
              (28,24),(20,19),(17,23),(10,17),(7,11),(11,8),(6,0)])
    elif kind=="cloud":
        d.arc((x,y+11*scale,x+15*scale,y+28*scale),90,270,fill=color,width=w)
        d.arc((x+7*scale,y+2*scale,x+26*scale,y+24*scale),170,355,fill=color,width=w)
        d.arc((x+20*scale,y+13*scale,x+33*scale,y+28*scale),270,90,fill=color,width=w)
        line([(7,28),(27,28)])
    elif kind=="apps":
        d.rounded_rectangle((x,y,x+26*scale,y+26*scale),3*scale,outline=color,width=w)
        line([(13,6),(13,20)]);line([(6,13),(20,13)])
    elif kind=="bell":
        d.arc((x+5*scale,y,x+23*scale,y+20*scale),180,360,fill=color,width=w)
        line([(5,9),(5,19),(1,24),(27,24),(23,19),(23,9)])
        d.arc((x+9*scale,y+22*scale,x+18*scale,y+29*scale),0,180,fill=color,width=w)


def linkedin():
    # Cropped post, like the supplied reference: no invented whole-site header.
    im=Image.new("RGB",(1100,1800),"white");d=ImageDraw.Draw(im)
    avatar(im,(25,25),96,color="#bdc8d4",blur=8)
    blurred_label(im,(139,29),"Alexandre Martin",32,330,42,True,radius=5)
    blurred_label(im,(139,75),"Product & Operations",26,470,38,fill="#666666",radius=5)
    d=ImageDraw.Draw(im)
    text(d,(484,29),"· 2nd",29,"#666666")
    text(d,(139,111),"1d ·",25,"#666666")
    d.ellipse((196,115,217,136),outline="#666666",width=2)
    d.arc((201,115,212,136),0,360,fill="#666666",width=1)
    d.line((196,125,217,125),fill="#666666",width=1)
    text(d,(902,33),"+ Follow",32,"#0a66c2",True)
    y=paragraph(d,(24,175),LINKEDIN_POST,1052,31,44)
    footer=y+30
    for x,c in [(39,"#378fe9"),(65,"#df704d"),(91,"#6d9e80")]:
        d.ellipse((x-19,footer,x+19,footer+38),fill=c,outline="white",width=2)
    icon(d,(26,footer+9),"like",.65,"white")
    text(d,(53,footer+5),"♥",24,"white")
    text(d,(82,footer+7),"✦",21,"white")
    text(d,(121,footer+8),"701",25,"#666666")
    text(d,(697,footer+8),"77 comments · 40 reposts",25,"#666666")
    d.line((24,footer+62,1076,footer+62),fill="#dedede",width=2)
    for cx,label,kind in [(143,"Like","like"),(414,"Comment","comment"),
                           (686,"Repost","repost"),(957,"Send","send")]:
        icon(d,(cx-19,footer+87),kind,1.3)
        width=d.textlength(label,font=font(27,True))
        text(d,(cx-width/2,footer+134),label,27,"#666666",True)
    height=footer+185
    im=im.crop((0,0,1100,height));ImageDraw.Draw(im).rounded_rectangle((1,1,1098,height-2),8,outline="#dedede",width=2)
    im.save(ROOT/"sample18.png",optimize=True)


def teams():
    # Reference: Microsoft's current combined Chat view, accessed October 2026.
    # Native editable UI reconstruction; every account and message is fictional.
    im=Image.new("RGB",(1800,1120),"#f5f5f5");d=ImageDraw.Draw(im)
    text(d,(24,17),"···",27,"#525252")
    text(d,(99,18),"Microsoft Teams",22,"#424242",True)
    d.rounded_rectangle((560,10,1230,54),8,fill="#e8e8ee")
    text(d,(584,20),"Search (Ctrl+E)",22,"#616161")
    text(d,(1650,17),"···   −   ×",24,"#616161")
    d.line((0,65,1800,65),fill="#dedede",width=1)
    d.rectangle((0,66,84,1120),fill="#ebebeb")
    for y,label,kind in [(110,"Activity","bell"),(209,"Chat","comment"),
                         (308,"Calendar","calendar"),(407,"Calls","phone"),
                         (506,"OneDrive","cloud"),(605,"Apps","apps")]:
        if label=="Chat":
            d.rectangle((0,y-15,4,y+68),fill="#5b5fc7")
            d.rounded_rectangle((11,y-10,74,y+62),7,fill="#e3e3f0")
        icon(d,(28,y),kind,1,color="#5b5fc7" if label=="Chat" else "#616161")
        fw=d.textlength(label,font=font(15));text(d,(42-fw/2,y+38),label,15,"#5b5fc7" if label=="Chat" else "#616161")
    # Combined Chat list with filters, Quick views and Favorites.
    d.rectangle((84,66,415,1120),fill="#f5f5f5")
    d.line((415,66,415,1120),fill="#dedede",width=1)
    text(d,(110,88),"Chat",30,bold=True);text(d,(281,90),"···   ⌕",26,"#616161")
    for x,label,width in [(108,"Unread",94),(213,"Chats",82),(306,"Channels",96)]:
        d.rounded_rectangle((x,148,x+width,187),20,outline="#c7c7c7",width=1)
        text(d,(x+12,157),label,20,"#484848")
    text(d,(109,215),"Quick views",20,"#616161")
    text(d,(123,256),"@  Mentions",22);text(d,(123,298),"Followed threads",22)
    text(d,(109,360),"Favorites",20,"#616161")
    text(d,(124,402),"General",22);text(d,(109,464),"Chats",20,"#616161")
    for i,name in enumerate(["Alexandre Martin","Camille Bernard","Morgan Lee"]):
        y=506+i*69
        if i==0:d.rounded_rectangle((101,y-9,399,y+49),6,fill="white",outline="#dfdfdf")
        avatar(im,(115,y),40,color="#c4ceda",blur=4)
        blurred_label(im,(168,y+5),name,22,218,35,bg="white" if i==0 else "#f5f5f5",radius=4)
    d=ImageDraw.Draw(im)
    text(d,(110,774),"Teams and channels",20,"#616161")
    text(d,(124,820),"Project office",22);text(d,(144,865),"General",21,"#616161")
    # Chat toolbar matches modern light Teams chrome, not the old purple bar.
    d.rectangle((416,66,1800,155),fill="white")
    avatar(im,(444,86),48,color="#c4ceda",blur=5)
    blurred_label(im,(506,94),"Alexandre Martin",27,280,40,True,radius=5)
    d=ImageDraw.Draw(im)
    text(d,(834,95),"Chat",23,"#242424",True);text(d,(910,95),"Shared",23,"#616161")
    text(d,(1010,95),"+",28,"#616161")
    d.line((834,151,881,151),fill="#5b5fc7",width=4)
    text(d,(1624,95),"Call  ∨   ···",23,"#616161")
    d.line((416,155,1800,155),fill="#dedede",width=1)
    text(d,(732,179),"Today",19,"#616161")
    # Incoming request + attached PDF. Outgoing validation is the purple bubble.
    avatar(im,(443,230),44,color="#c4ceda",blur=5)
    blurred_label(im,(503,222),"Alexandre Martin",21,226,34,bg="#f5f5f5",radius=4)
    d=ImageDraw.Draw(im);text(d,(741,223),"09:41",19,"#616161")
    d.rounded_rectangle((500,266,1145,483),8,fill="white")
    end=paragraph(d,(521,283),TEAMS_REQUEST,603,24,34)
    if end>467:raise ValueError("Teams request overflows; increase its bubble height.")
    d.rounded_rectangle((500,499,1075,579),7,fill="white",outline="#d8d8d8")
    d.rounded_rectangle((519,518,562,560),4,fill="#bd302f")
    text(d,(523,532),"PDF",15,"white",True)
    text(d,(578,513),"Q3_Final_Technical_Document.pdf",22,bold=True)
    text(d,(578,548),"84 KB",18,"#616161")
    blurred_label(im,(802,635),"Camille Bernard",21,245,33,bg="#f5f5f5",radius=4)
    d=ImageDraw.Draw(im);text(d,(1060,638),"09:42",19,"#616161")
    d.rounded_rectangle((518,680,1150,1022),8,fill="#e8ebfa")
    end=paragraph(d,(540,699),TEAMS_REPLY,588,24,34)
    if end>1007:raise ValueError("Teams reply overflows; increase its bubble height.")
    # Open document side panel. Its simple contents make the mismatch obvious.
    d.rectangle((1180,156,1800,1120),fill="white",outline="#dedede")
    text(d,(1202,177),"Q3_Final_Technical_Document.pdf",22,bold=True)
    text(d,(1750,176),"×",27,"#616161")
    d.line((1180,224,1800,224),fill="#dedede")
    text(d,(1251,245),"‹      1 / 1      ›         −    100%    +",23,"#616161")
    d.rectangle((1201,304,1778,1040),fill="#fafafa",outline="#d6d6d6")
    text(d,(1232,340),PDF_LINES[0],25,bold=True)
    text(d,(1232,392),PDF_LINES[1],31,bold=True)
    text(d,(1232,447),PDF_LINES[2],23,"#616161")
    d.line((1232,493,1747,493),fill="#dedede",width=2)
    yy=525
    for part in PDF_LINES[3:]:yy=paragraph(d,(1232,yy),part,512,24,35)+23
    if yy>1020:raise ValueError("PDF overflows; shorten PDF_LINES or adjust panel.")
    d.rounded_rectangle((467,1046,1150,1102),7,fill="white",outline="#b9b9b9")
    text(d,(485,1063),"Type a message",22,"#757575")
    icon(d,(1094,1061),"send",1,"#616161")
    im.save(ROOT/"sample19.png",optimize=True)


def tweet(value, filename, platform="X"):
    # Cropped post detail, native proportions and outline action icons.
    im=Image.new("RGB",(1200,1200),"white");d=ImageDraw.Draw(im)
    text(d,(30,20),"←",36);text(d,(123,23),"Post" if platform=="X" else "Truth",34,bold=True)
    if platform=="X":
        d.line((1107,25,1138,59),fill="#0f1419",width=5)
        d.line((1138,25,1107,59),fill="#0f1419",width=3)
    else:
        text(d,(1030,29),"TRUTH",25,"#4265e8",True)
    d.line((0,90,1200,90),fill="#eff3f4",width=2)
    avatar(im,(35,123),100,pixel_size=SOCIAL_AVATAR_PIXEL_SIZE)
    blurred_label(im,(155,126),"Donald J. Trump",35,410,48,True,
                  pixel_size=SOCIAL_NAME_PIXEL_SIZE)
    blurred_label(im,(155,179),"@realDonaldTrump",30,410,43,fill="#536471",
                  pixel_size=SOCIAL_NAME_PIXEL_SIZE)
    d=ImageDraw.Draw(im);text(d,(1112,126),"···",35,"#536471")
    end=paragraph(d,(35,269),value,1128,37,52,fill="#0f1419")
    footer=end+32
    d.line((35,footer,1165,footer),fill="#eff3f4",width=2)
    for x,kind in [(72,"comment"),(384,"repost"),(700,"heart"),(1100,"share")]:
        icon(d,(x,footer+25),kind,1.4,"#536471")
    height=footer+100
    im=im.crop((0,0,1200,height))
    ImageDraw.Draw(im).rectangle((0,0,1199,height-1),outline="#eff3f4",width=2)
    im.save(ROOT/filename,optimize=True)


if __name__ == "__main__":
    ROOT.mkdir(parents=True, exist_ok=True)
    linkedin()
    teams()
    tweet(GENUINE_TWEET, "sample21.png", platform="Truth Social")
    tweet(AI_TWEET, "sample22.png")
    print("Created static/images/sample18.png, sample19.png, sample21.png and sample22.png")
