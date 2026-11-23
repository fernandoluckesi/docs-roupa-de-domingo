# -*- coding: utf-8 -*-
"""Gera os criativos (PNG 1080x1350) e o legendas.txt.

Uso:  python3 build.py
Requer Google Chrome instalado (renderiza HTML em modo headless).
"""
import datetime as dt
import html
import os
import subprocess
import sys

from posts import ANUNCIO, POSTS

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)  # .../instagram/posts
ROOT = os.path.abspath(os.path.join(OUT, "..", "..", ".."))  # roupa-de-domingo/
FRONT = os.path.join(ROOT, "frontend-roupa-de-domingo")
PUBLIC = os.path.join(FRONT, "public")
FONTS = os.path.join(FRONT, "node_modules", "@fontsource")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
TMP = os.path.join(HERE, ".tmp")

DIAS = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]


def url(path):
    return "file://" + os.path.join(PUBLIC, path)


def font(fam, w):
    return f"file://{FONTS}/{fam}/files/{fam}-latin-{w}-normal.woff2"


CSS = f"""
@font-face{{font-family:Archivo;font-weight:600;src:url({font('archivo',600)})}}
@font-face{{font-family:Archivo;font-weight:800;src:url({font('archivo',800)})}}
@font-face{{font-family:Archivo;font-weight:900;src:url({font('archivo',900)})}}
@font-face{{font-family:Grotesk;font-weight:400;src:url({font('space-grotesk',400)})}}
@font-face{{font-family:Grotesk;font-weight:500;src:url({font('space-grotesk',500)})}}
@font-face{{font-family:Grotesk;font-weight:700;src:url({font('space-grotesk',700)})}}
:root{{--bg:#0f0f10;--soft:#17171a;--surf:#1e1e22;--line:#2e2e36;--txt:#f4f4f5;--mute:#a1a1aa;--lime:#d7ff3e;--ink:#121212}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:1080px;height:1350px;overflow:hidden;background:var(--bg)}}
body{{font-family:Grotesk,sans-serif;color:var(--txt);position:relative;
  background:radial-gradient(900px 600px at 85% -10%,rgba(215,255,62,.10),transparent 60%),var(--bg)}}
.wrap{{position:absolute;inset:0;padding:72px 72px 0;display:flex;flex-direction:column}}
.top{{display:flex;justify-content:space-between;align-items:center}}
.chip{{display:inline-block;background:var(--lime);color:var(--ink);font:700 22px/1 Grotesk;letter-spacing:.08em;
  padding:12px 18px;border-radius:999px;text-transform:uppercase}}
.chip.ghost{{background:transparent;color:var(--lime);border:2px solid var(--lime)}}
.logo{{text-align:right;line-height:1}}
.logo b{{font:800 30px/1 Archivo;display:block;letter-spacing:-.01em}}
.logo i{{font:700 13px/1 Grotesk;letter-spacing:.18em;color:var(--lime);font-style:normal;text-transform:uppercase}}
h1{{font:800 76px/1.02 Archivo;letter-spacing:-.025em;margin-top:44px}}
h1 em,.frase em{{font-style:normal;color:var(--lime)}}
.sub{{font:400 30px/1.35 Grotesk;color:var(--mute);margin-top:22px;max-width:900px}}
.card{{background:#fff;border-radius:28px;overflow:hidden;display:flex;align-items:center;justify-content:center}}
.card img{{width:100%;height:100%;object-fit:cover}}
.card.contain img{{object-fit:contain}}
.foot{{position:absolute;left:0;right:0;bottom:0;height:120px;padding:0 72px;display:flex;align-items:center;
  justify-content:space-between;border-top:1px solid var(--line);background:rgba(15,15,16,.92)}}
.foot .r{{font:500 25px/1.25 Grotesk;color:var(--mute);max-width:640px}}
.foot .u{{font:700 24px/1 Grotesk;color:var(--txt);white-space:nowrap}}
.foot .u span{{color:var(--lime)}}
.price{{position:absolute;background:var(--lime);color:var(--ink);font:800 44px/1 Archivo;padding:18px 26px;border-radius:18px;
  box-shadow:0 10px 30px rgba(0,0,0,.35);transform:rotate(-4deg)}}
.price small{{display:block;font:700 16px/1 Grotesk;letter-spacing:.12em;margin-bottom:6px}}
"""

FOOT = """<div class="foot"><div class="r">{r}</div><div class="u">roupadedomingo<span>.com.br</span></div></div>"""
TOP = """<div class="top"><span class="chip">{chip}</span>
<div class="logo"><b>Roupa de Domingo</b><i>estampas sem anestesia</i></div></div>"""


def card(i, extra=""):
    c = "card contain" if ("caneca" in i or "garrafa" in i) else "card"
    return f'<div class="{c}" {extra}><img src="{url(i)}" style="object-position:center 20%"></div>'


def price(p, style):
    return f'<div class="price" style="{style}"><small>A PARTIR DE</small>{p}</div>' if p else ""


def t_produto(p):
    return f"""{TOP.format(chip=p['chip'])}
<h1 style="font-size:{p.get('fs',70)}px">{p['titulo']}</h1>
{card(p['img'], f'style="position:absolute;left:72px;right:72px;top:{p.get("imgtop",470)}px;bottom:150px"')}
{price(p.get('preco'), 'right:100px;bottom:180px')}
{FOOT.format(r=p['rodape'])}"""


def t_frase(p):
    return f"""{TOP.format(chip=p['chip'])}
<div class="frase" style="font:900 {p.get('fs',90)}px/0.98 Archivo;letter-spacing:-.03em;margin-top:56px;max-width:936px;text-transform:uppercase">{p['frase']}</div>
<div class="card" style="position:absolute;right:-60px;bottom:120px;width:600px;height:600px;border-radius:40px 0 0 0">
<img src="{url(p['img'])}"></div>
<div style="position:absolute;left:72px;bottom:170px;font:700 22px/1.3 Grotesk;letter-spacing:.12em;color:var(--mute);max-width:300px">TEM NA<br><span style="color:var(--lime);font:800 40px/1.1 Archivo;letter-spacing:-.01em">LOJA</span><br>
<span style="font-size:60px;color:var(--txt)">↘</span></div>
{FOOT.format(r=p['rodape'])}"""


def t_chat(p):
    bubbles = ""
    for who, m in p["msgs"]:
        if who == "eu":
            bubbles += f'<div style="align-self:flex-end;background:var(--lime);color:var(--ink);font:800 50px/1.1 Archivo;padding:26px 34px;border-radius:34px 34px 8px 34px;max-width:620px">{m}</div>'
        else:
            bubbles += f'<div style="align-self:flex-start;background:var(--surf);border:1px solid var(--line);font:500 34px/1.2 Grotesk;padding:22px 30px;border-radius:30px 30px 30px 8px">{m}</div>'
    return f"""{TOP.format(chip=p['chip'])}
<div style="display:flex;flex-direction:column;gap:18px;margin-top:56px;width:100%">{bubbles}
<div style="align-self:flex-end;font:500 20px/1 Grotesk;color:var(--mute)">Visto ✓✓</div></div>
<div style="position:absolute;left:72px;right:72px;bottom:150px;height:430px;display:flex;gap:36px;align-items:center">
{card(p['img'], 'style="width:430px;height:430px;flex:none"')}
<div><div style="font:800 46px/1.08 Archivo;letter-spacing:-.02em">{p['titulo'].replace('<em>','<em style="font-style:normal;color:var(--lime)">')}</div>
<div style="margin-top:26px;display:inline-block;background:var(--lime);color:var(--ink);font:800 38px/1 Archivo;padding:14px 22px;border-radius:14px">{p['preco']}</div></div></div>
{FOOT.format(r='Caneca de cerâmica. Respostas prontas inclusas.')}"""


def t_lista(p):
    li = "".join(
        f'<li style="display:flex;gap:22px;align-items:baseline;padding:20px 0;border-bottom:1px solid var(--line)">'
        f'<span style="font:800 34px/1 Archivo;color:var(--lime);width:44px;flex:none">{i+1:02d}</span>'
        f'<span style="font:500 36px/1.2 Grotesk">{x}</span></li>' for i, x in enumerate(p["itens"]))
    return f"""{TOP.format(chip=p['chip'])}
<h1 style="font-size:66px">{p['titulo']}</h1>
<ul style="list-style:none;margin-top:30px;max-width:{p.get('lw',600)}px">{li}</ul>
<div style="position:absolute;left:72px;bottom:190px;max-width:500px;font:800 44px/1.08 Archivo;letter-spacing:-.02em">{p.get('nota','')}</div>
{card(p['img'], 'style="position:absolute;right:72px;bottom:150px;width:360px;height:440px;transform:rotate(3deg)"')}
{FOOT.format(r=p['rodape'])}"""


def t_grid(p):
    cells = "".join(card(i) for i in p["imgs"])
    return f"""{TOP.format(chip=p['chip'])}
<h1 style="font-size:{p.get('fs',72)}px">{p['titulo']}</h1>
<div class="sub">{p['sub']}</div>
<div style="flex:1;margin:48px 0 150px;display:grid;grid-template-columns:repeat(2,1fr);grid-template-rows:repeat(2,1fr);gap:18px;min-height:0">{cells}</div>
{FOOT.format(r=p['rodape'])}"""


def t_easter(p):
    return f"""{TOP.format(chip=p['chip'])}
<div style="font-size:150px;line-height:1;margin-top:50px">🥚</div>
<h1 style="font-size:84px;margin-top:24px">{p['titulo']}</h1>
<div class="sub" style="font-size:34px">{p['sub']}</div>
<div style="margin-top:56px;border:2px dashed var(--lime);border-radius:24px;padding:30px 34px">
<div style="font:700 20px/1 Grotesk;letter-spacing:.16em;color:var(--mute)">DICA GRATUITA (E NADA ÚTIL)</div>
<div style="font:800 58px/1.2 Archivo;color:var(--lime);margin-top:14px;letter-spacing:.04em">{p['dica']}</div></div>
<div style="position:absolute;right:72px;top:230px;font:800 30px/1 Archivo;background:var(--surf);border:1px solid var(--line);padding:22px 26px;border-radius:18px">🏆 0 de 8</div>
<div style="position:absolute;left:72px;bottom:170px;font:800 50px/1 Archivo;letter-spacing:-.02em">Achou? Comenta <span style="background:var(--lime);color:var(--ink);padding:4px 14px;border-radius:12px">ACHEI</span> 👇</div>
{FOOT.format(r=p['rodape'])}"""


def t_anuncio(p):
    cells = "".join(f'<div class="card"><img src="{url(i)}"></div>' for i in p["imgs"])
    selos = "".join(f'<span class="chip ghost" style="font-size:17px;padding:8px 14px">{s}</span>' for s in p["selos"])
    return f"""{TOP.format(chip=p['chip'])}
<h1 style="font-size:80px;margin-top:40px">{p['titulo']}</h1>
<div class="sub">{p['sub']}</div>
<div style="display:grid;grid-template-columns:1.25fr 1fr;grid-template-rows:1fr 1fr;gap:18px;flex:1;margin:36px 0 196px;min-height:0">
{card(p['imgs'][0], 'style="grid-row:span 2"')}{card(p['imgs'][1])}{card(p['imgs'][2])}</div>
<div style="position:absolute;left:72px;right:72px;bottom:40px;display:flex;justify-content:space-between;align-items:center">
<div style="display:flex;gap:8px;flex-direction:column;align-items:flex-start">{selos}</div>
<div style="background:var(--lime);color:var(--ink);font:800 36px/1 Archivo;padding:26px 34px;border-radius:999px;white-space:nowrap">{p['cta']}</div></div>"""


TEMPLATES = dict(produto=t_produto, frase=t_frase, chat=t_chat, lista=t_lista, grid=t_grid, easter=t_easter, anuncio=t_anuncio)


def nome(p):
    if p["template"] == "anuncio":
        return f"IMPULSIONAR_{p['data']}_{p['slug']}.png"
    return f"dia-{p['dia']:02d}_{p['data']}_{p['slug']}.png"


def check_imgs(p):
    for k in ("img", "imgs"):
        for i in ([p[k]] if k == "img" else p.get(k, [])) if k in p else []:
            if not os.path.exists(os.path.join(PUBLIC, i)):
                sys.exit(f"imagem não encontrada: {i}")


def render(p):
    check_imgs(p)
    body = TEMPLATES[p["template"]](p)
    doc = f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>{CSS}</style></head><body><div class="wrap">{body}</div></body></html>'
    os.makedirs(TMP, exist_ok=True)
    h = os.path.join(TMP, p["slug"] + ".html")
    open(h, "w", encoding="utf-8").write(doc)
    out = os.path.join(OUT, nome(p))
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
                    "--force-device-scale-factor=1", "--window-size=1080,1350", "--virtual-time-budget=4000",
                    f"--screenshot={out}", "file://" + h], check=True, capture_output=True)
    print("ok", nome(p))


def legendas():
    L = ["LEGENDAS - INSTAGRAM ROUPA DE DOMINGO",
         "Calendário: 20 posts de 23/11/2026 a 12/12/2026 + 1 criativo para impulsionar",
         "Formato de todas as imagens: feed 4:5 (1080x1350 px)",
         "Cada bloco começa com a data, o dia da semana e o nome exato do arquivo de imagem.", ""]
    sep = "=" * 72
    for p in POSTS:
        d = dt.date.fromisoformat(p["data"])
        L += [sep,
              f"DIA {p['dia']:02d}/20 | {d.strftime('%d/%m/%Y')} ({DIAS[d.weekday()]}) | sugestão de horário: {p.get('hora', '19h')}",
              f"IMAGEM: {nome(p)}",
              f"TEMA: {html.unescape(p['chip']).capitalize()} | PRODUTO: {p['produto']}",
              sep, "", p["legenda"].strip(), "", ""]
    a = ANUNCIO
    L += [sep, "CRIATIVO PARA IMPULSIONAR (ANÚNCIO) | começar em 23/11/2026 e rodar por 20 dias",
          f"IMAGEM: {nome(a)}",
          f"PRODUTO: {a['produto']} | Botão sugerido: Comprar agora → roupadedomingo.com.br",
          "Público sugerido: 18-40 anos, Brasil, interesses em humor, memes, stand-up, camisetas e presentes",
          "Observação: criativo sem palavrão, sem política e sem piada de aparência, para passar na revisão de anúncios da Meta.",
          sep, "", a["legenda"].strip(), ""]
    open(os.path.join(OUT, "legendas.txt"), "w", encoding="utf-8").write("\n".join(L))
    print("ok legendas.txt")


if __name__ == "__main__":
    only = sys.argv[1:]
    for p in POSTS + [ANUNCIO]:
        if not only or p["slug"] in only:
            render(p)
    legendas()
