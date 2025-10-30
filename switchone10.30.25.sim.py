#!/usr/bin/env python3
"""
Switch One GUI 2.0 – Slates, Themes & Trophies
Author: Catsan / FlamesCoOS Labs

Patch notes:
- Switch-accurate colors: Joy-Con Neon Blue (#0AB9E6), Neon Red (#FF3C28),
  and Nintendo Red accent (#E60012).
- File I/O OFF: no reads/writes; state is in-memory only.
- Fixed 'Themes' screen click hitboxes (they now use absolute window coords).
"""

import pygame, pygame.freetype, random, datetime

# --- CONFIG ------------------------------------------------
WIN_W, WIN_H = 600, 400
SCREEN_W, SCREEN_H = 460, 260
SCREEN_X, SCREEN_Y = (WIN_W - SCREEN_W)//2, 70
FPS = 60
BEZEL_RADIUS = 20

# === SWITCH-ACCURATE PALETTE =========================================
# Joy-Con: Neon Blue (#0AB9E6), Neon Red (#FF3C28)
# Accent / Brand: Nintendo Red (#E60012)
THEMES = {
    "switch_dark": {
        "BG":   (16, 16, 16),          # near-black UI background
        "ACC":  (230, 0, 18),          # Nintendo Red
        "JOY_L":(10, 185, 230),        # Neon Blue
        "JOY_R":(255, 60, 40),         # Neon Red
    },
    "switch_light": {
        "BG":   (247, 247, 247),       # light UI background
        "ACC":  (230, 0, 18),          # Nintendo Red
        "JOY_L":(10, 185, 230),
        "JOY_R":(255, 60, 40),
    },
    "synth": {                         # keep your fun theme too
        "BG":   (10, 0, 20),
        "ACC":  (255, 0, 200),
        "JOY_L":(80, 0, 255),
        "JOY_R":(255, 0, 120),
    },
}
theme_name = "switch_dark"

def yiq_luma(rgb):
    r,g,b = rgb
    return (r*299 + g*587 + b*114) / 1000

def compute_text_color(bg):
    return (255,255,255) if yiq_luma(bg) < 140 else (20,20,20)

def compute_bar_color(bg):
    # Slightly offset from BG for top/bottom bars
    if yiq_luma(bg) < 140:  # dark
        return tuple(min(255, c+6) for c in bg)
    else:                    # light
        return tuple(max(0, c-20) for c in bg)

# pygame setup
pygame.init(); pygame.freetype.init()
screen = pygame.display.set_mode((WIN_W, WIN_H), pygame.HWSURFACE|pygame.DOUBLEBUF)
pygame.display.set_caption("Switch One 2.0 – Slates Firmware Simulation")
clock = pygame.time.Clock()

FONT_S = pygame.freetype.SysFont("segoeui",16)
FONT_B = pygame.freetype.SysFont("segoeui",22,bold=True)
FONT_I = pygame.freetype.SysFont("segoeui",48,bold=True)
FONT_L = pygame.freetype.SysFont("segoeui",14)

# --- STATE (files OFF: purely in-memory) -------------------
brightness = 1.0
volume     = 0.7

def update_theme_globals():
    global BG_COLOR, ACCENT_COLOR, JOYCON_L, JOYCON_R, TEXT_COLOR, BAR_COLOR
    BG_COLOR, ACCENT_COLOR, JOYCON_L, JOYCON_R = (
        THEMES[theme_name][k] for k in ("BG","ACC","JOY_L","JOY_R")
    )
    TEXT_COLOR = compute_text_color(BG_COLOR)
    BAR_COLOR  = compute_bar_color(BG_COLOR)

update_theme_globals()

current_screen = "home"
selected = None
hovered  = None
album_imgs = []
trophies   = ["🎖️ First Launch","🏆 Mario Kart Played","⭐ 100% Brightness"]
firmwares  = ["SlateOS v1.0.0 (Launch)","SlateOS v1.1.2 Flames Update","SlateOS v1.2.0 Harmony Build"]
friends    = ["Friend1","Friend2"]

ICONS = [
    ("🎮","Games","games"),("🛍️","eShop","eshop"),("📸","Album","album"),
    ("⚙️","Settings","settings"),("🌐","News","news"),("👤","Profile","profile"),
    ("🎨","Themes","themes"),("🏆","Trophies","trophies"),("💽","Slates","slates"),
    ("🔧","System","system"),("💾","Data","data"),("❓","Help","help")
]

# --- HELPERS -----------------------------------------------
def draw_rr(surf,r,color,b=0): pygame.draw.rect(surf,color,r,border_radius=b)
def get_icon_rect(i,startx=SCREEN_X+30,starty=SCREEN_Y+50,sp=85,cols=6):
    r=i//cols; c=i%cols; return pygame.Rect(startx+c*sp,starty+r*sp,70,70)
def apply_brightness(s):
    dim=pygame.Surface(s.get_size(),pygame.SRCALPHA)
    dim.fill((0,0,0,int(255*(1-brightness)))); s.blit(dim,(0,0))

def fade_transition():
    overlay=pygame.Surface(screen.get_size()); overlay.fill(BG_COLOR)
    for a in range(0,255,20):
        overlay.set_alpha(a); screen.blit(overlay,(0,0))
        pygame.display.flip(); clock.tick(60)

# --- DRAW --------------------------------------------------
def draw_home(s):
    for i,(e,l,_) in enumerate(ICONS):
        r=get_icon_rect(i)
        if hovered==i:
            glow=pygame.Surface((70,70),pygame.SRCALPHA)
            glow.fill((255,255,255,60 if yiq_luma(BG_COLOR)<140 else 40))
            s.blit(glow,(r.x-SCREEN_X,r.y-SCREEN_Y))
        if selected==i:
            pygame.draw.rect(s,ACCENT_COLOR,(r.x-SCREEN_X,r.y-SCREEN_Y,70,70),3,12)
        FONT_I.render_to(s,(r.centerx-SCREEN_X-20,r.centery-SCREEN_Y-30),e,TEXT_COLOR)
        w=FONT_L.get_rect(l).width
        FONT_L.render_to(s,(r.centerx-SCREEN_X-w//2,r.centery-SCREEN_Y+20),l,TEXT_COLOR)

def draw_themes(s):
    FONT_B.render_to(s,(20,20),"Themes",TEXT_COLOR)
    y=60
    for name in THEMES.keys():
        box=pygame.Rect(20,y,200,30)
        color=THEMES[name]["ACC"]
        pygame.draw.rect(s,color,box,border_radius=8)
        if theme_name==name: pygame.draw.rect(s,(255,255,255),box,3,border_radius=8)
        FONT_L.render_to(s,(30,y+6),name.upper(),(0,0,0) if yiq_luma(color)<140 else (0,0,0))
        y+=40

def draw_trophies(s):
    FONT_B.render_to(s,(20,20),"Trophies",TEXT_COLOR)
    for i,t in enumerate(trophies):
        FONT_S.render_to(s,(30,60+i*30),t,ACCENT_COLOR)

def draw_slates(s):
    FONT_B.render_to(s,(20,20),"Slates Firmware Manager",TEXT_COLOR)
    for i,f in enumerate(firmwares):
        FONT_S.render_to(s,(30,60+i*25),f,TEXT_COLOR)
    FONT_L.render_to(s,(20,160),"Current: "+firmwares[-1],ACCENT_COLOR)
    FONT_L.render_to(s,(20,190),"Status: Up to date ✓",ACCENT_COLOR)

def draw_screen():
    bezel=pygame.Rect(SCREEN_X-10,SCREEN_Y-10,SCREEN_W+20,SCREEN_H+20)
    draw_rr(screen,bezel,(24,24,24) if yiq_luma(BG_COLOR)<140 else (210,210,210),BEZEL_RADIUS)
    surf=pygame.Surface((SCREEN_W,SCREEN_H),pygame.SRCALPHA)
    surf.fill(BG_COLOR)
    if current_screen=="home": draw_home(surf)
    elif current_screen=="themes": draw_themes(surf)
    elif current_screen=="trophies": draw_trophies(surf)
    elif current_screen=="slates": draw_slates(surf)
    else: FONT_B.render_to(surf,(20,20),current_screen.capitalize(),TEXT_COLOR)
    apply_brightness(surf); screen.blit(surf,(SCREEN_X,SCREEN_Y))

def draw_hud():
    pygame.draw.rect(screen,BAR_COLOR,(0,0,WIN_W,50))
    FONT_B.render_to(screen,(15,8),"Switch One 2.0",TEXT_COLOR)
    now=datetime.datetime.now().strftime("%H:%M")
    FONT_S.render_to(screen,(WIN_W-100,15),now,TEXT_COLOR)

def draw_bottom():
    y=WIN_H-25
    pygame.draw.rect(screen,BAR_COLOR,(0,WIN_H-50,WIN_W,50))
    pygame.draw.circle(screen,ACCENT_COLOR,(WIN_W//2-25,y),18,2)
    FONT_I.render_to(screen,(WIN_W//2-37,y-18),"🏠",ACCENT_COLOR)
    pygame.draw.circle(screen,ACCENT_COLOR,(WIN_W-80,y),18,2)
    FONT_I.render_to(screen,(WIN_W-90,y-18),"⏻",ACCENT_COLOR)
    pygame.draw.rect(screen,(60,60,60) if yiq_luma(BG_COLOR)<140 else (180,180,180),
                     (60,WIN_H-35,100,20),border_radius=10)
    pygame.draw.rect(screen,ACCENT_COLOR,(60,WIN_H-35,int(100*volume),20),border_radius=10)

# --- LOOP ---------------------------------------------------
running=True
while running:
    mx,my=pygame.mouse.get_pos(); hovered=None
    for e in pygame.event.get():
        if e.type==pygame.QUIT:
            running=False

        elif e.type==pygame.KEYDOWN:
            if e.key==pygame.K_ESCAPE:
                if current_screen!="home":
                    current_screen="home"; selected=None; fade_transition()
            elif e.key==pygame.K_c:
                album_imgs.append({"color":(random.randint(0,255),random.randint(0,255),random.randint(0,255))})

        elif e.type==pygame.MOUSEBUTTONDOWN:
            if current_screen=="home":
                for i,(_,_,id_) in enumerate(ICONS):
                    if get_icon_rect(i).collidepoint(mx,my):
                        current_screen=id_; selected=i; fade_transition()
            elif current_screen=="themes":
                # FIXED: hitboxes in absolute coordinates
                y=60
                for name in THEMES.keys():
                    rect_abs = pygame.Rect(SCREEN_X+20, SCREEN_Y+y, 200, 30)
                    if rect_abs.collidepoint(mx,my):
                        theme_name=name
                        update_theme_globals()
                        fade_transition()
                    y+=40

        elif e.type==pygame.MOUSEMOTION:
            if current_screen=="home":
                for i in range(len(ICONS)):
                    if get_icon_rect(i).collidepoint(mx,my): hovered=i; break

    screen.fill(BG_COLOR)
    draw_screen(); draw_hud(); draw_bottom()
    pygame.display.flip(); clock.tick(FPS)

pygame.quit()
