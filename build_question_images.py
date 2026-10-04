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
    "Validated. The document establishes a fault-tolerant "
    "distributed consensus architecture with Raft leader election and "
    "Byzantine resilience. I particularly appreciated the homomorphic "
    "encryption layer, the quantum-safe key exchange and the Kubernetes "
    "service mesh. Ready for planetary-scale deployment. No changes needed."
)
PDF_LINES = [
    "Q3 PROJECT WRAP-UP", "Office coffee rota", "Final technical document",
    "One shared spreadsheet. Three columns:", "Name | Week | Refill beans",
    "Everyone edits their own row manually.", "Friday: check next week's volunteer.",
    "Success: no empty coffee machine.", "No servers. No API. No automation.",
]
GENUINE_TWEET = "I have never seen a thin person drinking Diet Coke."
GENUINE_TWEET_SOURCE = "https://x.com/realDonaldTrump/status/257552283850653696"
AI_TWEET = (
    "We will build the biggest FIREWALL anyone has ever seen. Beautiful firewall. "
    "And the hackers are going to pay for it. They said nobody could secure a "
    "network with CAPS LOCK. WRONG!"
)


def font(size, bold=False):
    names = ["DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
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


def identity(image, xy, color="#88a4b0", name_width=215, size=58):
    x, y = xy
    avatar = Image.new("RGB", (size, size), color)
    ad = ImageDraw.Draw(avatar)
    ad.ellipse((size*.31, size*.13, size*.7, size*.54), fill="#dcc3ab")
    ad.ellipse((size*.12, size*.48, size*.91, size*1.2), fill="#334858")
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    image.paste(avatar.filter(ImageFilter.GaussianBlur(9)), (x, y), mask)
    label = Image.new("RGB", (name_width, 52), "white")
    ld = ImageDraw.Draw(label)
    text(ld, (0, -2), "Alexandre Martin", 23, bold=True)
    text(ld, (0, 28), "Product & Operations", 18, "#666666")
    image.paste(label.filter(ImageFilter.GaussianBlur(7)), (x + size + 14, y + 2))


def linkedin():
    im = Image.new("RGB", (1100, 1110), "#f3f2ef")
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 1100, 82), fill="white")
    d.rounded_rectangle((36, 17, 82, 63), radius=4, fill="#0a66c2")
    text(d, (43, 15), "in", 36, "white", True)
    d.rounded_rectangle((100, 17, 405, 63), radius=4, fill="#edf3f8")
    text(d, (120, 26), "Search", 22, "#5d666c")
    for x, icon, label in [(466, "⌂", "Home"), (585, "♙", "My Network"),
                            (715, "▣", "Jobs"), (820, "□", "Messaging"), (970, "●", "Notifications")]:
        text(d, (x, 3), icon, 29, "#666666")
        text(d, (x-20, 49), label, 15, "#666666")
    d.rounded_rectangle((85, 108, 1015, 1068), radius=12, fill="white", outline="#d7d7d7", width=2)
    identity(im, (115, 137), size=76, name_width=275)
    d = ImageDraw.Draw(im)
    text(d, (205, 202), "1d · ◉", 19, "#777777")
    text(d, (927, 131), "···", 35, "#666666")
    y = paragraph(d, (120, 257), LINKEDIN_POST, 850, 29, 43)
    footer_y = max(895, y + 22)
    for cx, c, s in [(137, "#378fe9", "+"), (159, "#df704d", "♥"), (181, "#6d9e80", "★")]:
        d.ellipse((cx-16, footer_y, cx+16, footer_y+32), fill=c, outline="white", width=2)
        text(d, (cx-8, footer_y+4), s, 16, "white")
    text(d, (208, footer_y+4), "1,284", 19, "#666666")
    text(d, (647, footer_y+4), "86 comments · 24 reposts", 19, "#666666")
    d.line((116, footer_y+52, 983, footer_y+52), fill="#dddddd", width=2)
    for x, label in [(145, "♡  Like"), (353, "□  Comment"), (591, "⇄  Repost"), (815, "➤  Send")]:
        text(d, (x, footer_y+75), label, 22, "#666666", True)
    im.save(ROOT / "sample18.png", optimize=True)


def teams():
    im = Image.new("RGB", (1560, 1070), "#f5f5f5")
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 1560, 66), fill="#48466d")
    text(d, (24, 16), "···    Microsoft Teams", 24, "white", True)
    d.rounded_rectangle((444, 12, 1115, 53), radius=6, fill="#e8e8ef")
    text(d, (466, 20), "Search (Ctrl+E)", 21, "#6b6b78")
    d.rectangle((0, 66, 86, 1070), fill="#eeeeF4")
    for y, icon, label in [(105, "●", "Activity"), (204, "□", "Chat"), (303, "▣", "Teams"), (402, "▦", "Calendar"), (501, "☎", "Calls")]:
        text(d, (30, y), icon, 26, "#6264a7")
        text(d, (9, y+38), label, 14, "#555561")
    d.rectangle((86, 66, 1560, 149), fill="white")
    identity(im, (114, 83), "#bea7c8", size=46, name_width=236)
    d = ImageDraw.Draw(im)
    text(d, (477, 98), "Chat     Shared     +", 24, "#5b5fc7")
    text(d, (1364, 98), "◉    ☎    ···", 25, "#666666")
    text(d, (698, 174), "Thursday, 3 October", 18, "#787884")
    # Left: actual conversation. Right: the opened, extremely simple PDF.
    identity(im, (114, 215), "#90aab2", size=46, name_width=210)
    d = ImageDraw.Draw(im)
    text(d, (393, 223), "09:41", 18, "#787884")
    d.rounded_rectangle((176, 279, 905, 511), radius=8, fill="white")
    paragraph(d, (197, 297), TEAMS_REQUEST, 687, 25, 36)
    d.rounded_rectangle((176, 527, 842, 609), radius=8, fill="white", outline="#d6d6dd", width=2)
    d.rounded_rectangle((195, 545, 242, 592), radius=5, fill="#ca3838")
    text(d, (201, 558), "PDF", 15, "white", True)
    text(d, (260, 541), "Q3_Final_Technical_Document.pdf", 22, bold=True)
    text(d, (260, 575), "1 page · 84 KB", 17, "#777777")
    identity(im, (114, 641), "#b6a183", size=46, name_width=210)
    d = ImageDraw.Draw(im)
    text(d, (393, 650), "09:42", 18, "#787884")
    d.rounded_rectangle((176, 707, 905, 978), radius=8, fill="white")
    paragraph(d, (197, 725), TEAMS_REPLY, 687, 25, 36)
    # Shared document preview. Labels are part of the fictional Teams chrome.
    d.rounded_rectangle((937, 213, 1532, 979), radius=8, fill="#e7e7ec", outline="#d0d0d6")
    text(d, (954, 231), "Q3_Final_Technical_Document.pdf", 19, bold=True)
    text(d, (978, 279), "‹    1 / 1          100%                ×", 21, "#666666")
    d.rectangle((960, 322, 1509, 952), fill="white")
    text(d, (988, 356), PDF_LINES[0], 25, bold=True)
    text(d, (988, 405), PDF_LINES[1], 28, bold=True)
    text(d, (988, 454), PDF_LINES[2], 21, "#666666")
    d.line((988, 496, 1480, 496), fill="#cccccc", width=2)
    yy = 526
    for part in PDF_LINES[3:]:
        yy = paragraph(d, (988, yy), part, 488, 23, 34) + 20
    d.rounded_rectangle((176, 1005, 1532, 1054), radius=5, fill="white", outline="#b8b8c4")
    text(d, (194, 1018), "Type a message", 20, "#8b8b91")
    im.save(ROOT / "sample19.png", optimize=True)


def tweet(value, filename):
    """Identical anonymized layouts: no date, counts or account clue to the answer."""
    im = Image.new("RGB", (1200, 720), "#f5f8fa")
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((40, 36, 1160, 684), radius=16, fill="white", outline="#dfe6eb", width=2)
    text(d, (86, 61), "Tweet", 27, "#657786", True)
    d.line((68, 112, 1132, 112), fill="#e8eef2", width=2)
    identity(im, (86, 143), color="#aec4d1", name_width=335, size=82)
    # Blur the author's name and handle; no readable profile identifiers survive.
    identity_strip = Image.new("RGB", (360, 76), "white")
    sd = ImageDraw.Draw(identity_strip)
    text(sd, (4, 0), "Donald J. Trump", 29, bold=True)
    text(sd, (4, 42), "@realDonaldTrump", 25, "#657786")
    im.paste(identity_strip.filter(ImageFilter.GaussianBlur(11)), (182, 146))
    d = ImageDraw.Draw(im)
    text(d, (1082, 139), "···", 35, "#657786")
    end = paragraph(d, (86, 285), value, 1028, size=42, line=62, fill="#14171a")
    if end > 573:
        raise ValueError(f"Tweet text overflows {filename}; shorten it or adjust the template.")
    d.line((86, 586, 1114, 586), fill="#e8eef2", width=2)
    for x in (125, 422, 715, 1034):
        # Reply, retweet, like, share icons; no invented engagement numbers.
        if x == 125:
            d.rounded_rectangle((x, 613, x+34, 641), radius=7, outline="#657786", width=3)
            d.line((x+7, 641, x+3, 650, x+17, 641), fill="#657786", width=3)
        elif x == 422:
            text(d, (x-2, 605), "⇄", 39, "#657786")
        elif x == 715:
            text(d, (x-2, 607), "♡", 36, "#657786")
        else:
            d.line((x, 626, x, 648, x+30, 648, x+30, 626), fill="#657786", width=3)
            d.line((x+15, 639, x+15, 610), fill="#657786", width=3)
            d.line((x+6, 620, x+15, 610, x+24, 620), fill="#657786", width=3)
    im.save(ROOT / filename, optimize=True)


if __name__ == "__main__":
    ROOT.mkdir(parents=True, exist_ok=True)
    linkedin()
    teams()
    tweet(GENUINE_TWEET, "sample21.png")
    tweet(AI_TWEET, "sample22.png")
    print("Created static/images/sample18.png, sample19.png, sample21.png and sample22.png")
