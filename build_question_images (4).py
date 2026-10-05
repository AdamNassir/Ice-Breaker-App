"""Rebuild the three social screenshots and code card: python build_question_images.py.

Optional authoring dependency only: python -m pip install Pillow
Macron and Teams messages are in French; interface labels remain English.
The deployed game uses the bundled PNGs and does not need Pillow.
Edit LINKEDIN_POST, TEAMS_REQUEST, TEAMS_REPLY, or AI_TWEET below.
AI_SQL is original AI-written SQL; SQL_STYLE_SOURCE credits its formatting reference.
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
    "Bonjour, voici le bilan de mon stage. L'outil permet de poser une question "
    "sur les documents techniques et de retrouver les passages utiles. Le rapport "
    "présente la lecture des PDF, l'organisation des informations et les essais. "
    "Peux-tu valider le document avant mon départ ?"
)
TEAMS_REPLY = (
    "C'est validé, merci. Le rapport montre bien que l'outil peut surveiller "
    "les avions en vol et décider des réparations à effectuer. La recherche "
    "hybride permettra aussi de passer automatiquement du moteur électrique "
    "au réacteur. On peut donc lancer les essais sur la flotte. Beau travail !"
)
# Original AI rewrite of the PostgreSQL aggregate-query pattern.
# Preserve uppercase clauses, lowercase names and four-space clause indentation.
AI_SQL = """SELECT department, count(*) AS headcount,
       round(avg(annual_salary), 2) AS average_salary
    FROM employees
    WHERE employment_status = 'active'
    GROUP BY department
    HAVING count(*) >= 5
    ORDER BY average_salary DESC;"""
SQL_STYLE_SOURCE = "https://www.postgresql.org/docs/current/tutorial-agg.html"
AI_TWEET = (
    "Dès janvier, dix hôpitaux expérimenteront une intelligence artificielle "
    "développée en France pour anticiper l'affluence aux urgences. "
    "Elle s'appuiera sur des données anonymisées. "
    "Mieux prévoir pour mieux soigner, sans jamais remplacer les soignants. "
    "C'est le sens de notre ambition.\n\n#Santé #IA #France2030"
)
# Actual profile picture supplied by the presenter; only the post writing is AI fiction.
# Origin and exact crop details: ContentSources.md. No actual policy is asserted.
MACRON_PORTRAIT = ROOT / "profile-source.png"


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


# CHANGE these block sizes for legacy Trump cards (not in the active deck). Larger blocks hide more.
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
    text(d,(1080,179),"Today",19,"#616161")
    # Expanded chat: attachment only, no open-document panel.
    def height(value, width):
        return paragraph(ImageDraw.Draw(Image.new("RGB",(1,1))), (0,0), value,
                         width, 30, 43)
    avatar(im,(443,230),44,color="#c4ceda",blur=5)
    blurred_label(im,(503,222),"Alexandre Martin",23,245,34,bg="#f5f5f5",radius=4)
    d=ImageDraw.Draw(im);text(d,(771,223),"09:41",20,"#616161")
    request_bottom=286+height(TEAMS_REQUEST,1192)+18
    d.rounded_rectangle((500,266,1738,request_bottom),8,fill="white")
    paragraph(d,(523,286),TEAMS_REQUEST,1192,30,43)
    pdf_y=request_bottom+16
    d.rounded_rectangle((500,pdf_y,1230,pdf_y+88),7,fill="white",outline="#d8d8d8")
    d.rounded_rectangle((519,pdf_y+21,568,pdf_y+68),4,fill="#bd302f")
    text(d,(526,pdf_y+35),"PDF",16,"white",True)
    text(d,(589,pdf_y+17),"Bilan_Stage_Recherche_Documents.pdf",28,bold=True)
    text(d,(589,pdf_y+55),"84 KB",20,"#616161")
    reply_y=pdf_y+158
    blurred_label(im,(1338,reply_y-44),"Camille Bernard",23,245,34,bg="#f5f5f5",radius=4)
    d=ImageDraw.Draw(im);text(d,(1600,reply_y-42),"Manager · 09:42",19,"#616161")
    reply_bottom=reply_y+22+height(TEAMS_REPLY,1070)+18
    d.rounded_rectangle((620,reply_y,1738,reply_bottom),8,fill="#e8ebfa")
    paragraph(d,(644,reply_y+22),TEAMS_REPLY,1070,30,43)
    input_y=reply_bottom+38
    d.rounded_rectangle((467,input_y,1738,input_y+60),7,fill="white",outline="#b9b9b9")
    text(d,(486,input_y+19),"Type a message",24,"#757575")
    icon(d,(1681,input_y+17),"send",1.1,"#616161")
    final_height=max(960,input_y+79)
    if final_height>1120:raise ValueError("Teams messages overflow; adjust text/size.")
    im=im.crop((0,0,1800,final_height))
    im.save(ROOT/"sample19.png",optimize=True)


def code_card():
    """Bare SQL, in the clause layout of the PostgreSQL tutorial reference."""
    lines = AI_SQL.splitlines()
    height = 120 + len(lines) * 58
    im = Image.new("RGB", (1600, height), "white")
    d = ImageDraw.Draw(im)
    d.rectangle((46, 30, 1554, height - 30), fill="#f5f5f5", outline="#dddddd", width=2)
    names = ["DejaVuSansMono.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
             str(Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / "consola.ttf"),
             "/System/Library/Fonts/Menlo.ttc"]
    face = None
    for name in names:
        try: face = ImageFont.truetype(name, 38); break
        except OSError: pass
    if face is None: face = ImageFont.load_default(size=38)
    # Draw unchanged whitespace and text; no title, scenario, comments or source clues.
    for row, line in enumerate(lines):
        if d.textlength(line, font=face) > 1438: raise ValueError("Code line overflows the card.")
        d.text((81, 60 + row * 58), line, font=face, fill="#222222")
    im.save(ROOT / "sample23.png", optimize=True)


def tweet(value, filename, platform="X", macron=False):
    # Native UI reconstruction of the two user-supplied post references.
    dark=platform=="X"
    bg="#000000" if dark else "#ffffff"
    ink="#e7e9ea" if dark else "#181818"
    muted="#71767b" if dark else "#858585"
    im=Image.new("RGB",(1200,1500),bg);d=ImageDraw.Draw(im)
    if dark:
        text(d,(41,27),"←",38,ink);text(d,(151,28),"Post",40,ink,True)
        avatar_y,name_y,handle_y,body_y=127,130,173,291
    else:
        avatar_y,name_y,handle_y,body_y=20,23,67,174
    if macron:
        # Extract the circular profile photo from the supplied screenshot; no blur.
        with Image.open(MACRON_PORTRAIT) as portrait:
            tile = portrait.convert("RGB").crop((32, 13, 398, 379)).resize((80, 80), Image.Resampling.LANCZOS)
        mask = Image.new("L", (80, 80), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, 79, 79), fill=255)
        im.paste(tile, (31, avatar_y), mask)
        text(d, (132, name_y), "Emmanuel Macron", 32, ink, True)
        text(d, (132, handle_y), "@EmmanuelMacron", 29, muted)
    else:
        avatar(im,(31,avatar_y),80,pixel_size=SOCIAL_AVATAR_PIXEL_SIZE)
        blurred_label(im,(132,name_y),"Donald J. Trump",32,370,44,True,
                      bg=bg,fill=ink,pixel_size=SOCIAL_NAME_PIXEL_SIZE)
        blurred_label(im,(132,handle_y),"@realDonaldTrump",29,370,42,
                      bg=bg,fill=muted,pixel_size=SOCIAL_NAME_PIXEL_SIZE)
    d=ImageDraw.Draw(im)
    # Verification badges sit outside the pixelated identity fields.
    badge_y=name_y+16;badge_color="#1d9bf0" if macron else ("#829ba9" if dark else "#e8527b")
    points=[]
    import math
    for n in range(24):
        angle=n*math.pi/12;r=16 if n%2==0 else 13
        points.append((529+math.cos(angle)*r,badge_y+math.sin(angle)*r))
    d.polygon(points,fill=badge_color)
    d.line((521,badge_y,527,badge_y+5,538,badge_y-6),fill=bg,width=3)
    if dark:
        text(d,(1132,139),"···",29,muted)
        text(d,(43,245),"Translate post",25,"#1d9bf0")
    else:
        d.rounded_rectangle((564,name_y+2,595,name_y+31),6,fill="#101016")
        text(d,(572,name_y+1),"+",25,"white",True)
    body, separator, tags = value.partition("\n\n#")
    end=paragraph(d,(29,body_y),body,1135,37,49,ink)
    if separator:
        end=paragraph(d,(29,end+20),"#"+tags,1135,37,49,"#1d9bf0")
    if dark:
        footer=end+35
        d.line((29,footer,1170,footer),fill="#2f3336",width=2)
        for x,kind in [(42,"comment"),(318,"repost"),(596,"heart"),(1101,"share")]:
            icon(d,(x,footer+28),kind,1.35,muted)
        # Bookmark outline, matching the supplied dark X screenshot.
        d.line((875,footer+30,903,footer+30,903,footer+67,889,footer+57,
                875,footer+67,875,footer+30),fill=muted,width=3)
        final_height=footer+98
    else:
        final_height=end+24
    im=im.crop((0,0,1200,final_height))
    im.save(ROOT/filename,optimize=True)


if __name__ == "__main__":
    ROOT.mkdir(parents=True, exist_ok=True)
    linkedin()
    teams()
    code_card()
    tweet(AI_TWEET, "sample27.png", macron=True)
    print("Created static/images/sample18.png, sample19.png, sample23.png and sample27.png")
