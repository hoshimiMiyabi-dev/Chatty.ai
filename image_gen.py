import io
from PIL import Image, ImageDraw
from utils import get_font

def create_ping_card(avatar_bytes: bytes, bot_name: str, ws_ping: int, groq_ping: int) -> io.BytesIO:
    scale = 2
    card_w, card_h = 600 * scale, 420 * scale  
    
    base = Image.new("RGBA", (card_w, card_h), (8, 10, 14, 255))
    overlay = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    
    overlay_draw.rounded_rectangle(
        [10 * scale, 10 * scale, card_w - (10 * scale), card_h - (10 * scale)],
        radius=16 * scale,
        fill=(14, 16, 22, 235),
        outline=(59, 130, 246),  # Modern Blue Accent
        width=2 * scale
    )
    
    base = Image.alpha_composite(base, overlay)
    draw = ImageDraw.Draw(base)

    f_sub = get_font(12 * scale)
    f_title = get_font(26 * scale)
    f_val = get_font(18 * scale)
    f_footer = get_font(12 * scale)

    avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
    avatar_size = (110 * scale, 110 * scale)
    avatar = avatar.resize(avatar_size, Image.Resampling.LANCZOS)

    mask = Image.new("L", avatar_size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, avatar_size[0], avatar_size[1]), fill=255)

    base.paste(avatar, (35 * scale, 30 * scale), mask)

    draw.text((180 * scale, 42 * scale), "SYSTEM STATUS", fill=(140, 150, 170), font=f_sub)
    draw.text((180 * scale, 65 * scale), bot_name.upper(), fill=(255, 255, 255), font=f_title)
    draw.line([35 * scale, 135 * scale, card_w - (35 * scale), 135 * scale], fill=(40, 45, 55), width=1 * scale)

    def get_status_theme(ping_value):
        if ping_value < 150: return (0, 240, 255), "OPTIMAL"
        elif ping_value < 300: return (255, 170, 0), "MODERATE"
        else: return (255, 60, 80), "HIGH LATENCY"

    ws_color, ws_status = get_status_theme(ws_ping)
    groq_color, groq_status = get_status_theme(groq_ping)

    def draw_metric_block(start_y, label, ping_val, status_str, color):
        content_x = 35 * scale
        panel_w = card_w - (70 * scale)
        
        draw.rounded_rectangle(
            [content_x, start_y, content_x + panel_w, start_y + (85 * scale)],
            radius=12 * scale, fill=(20, 24, 32), outline=(45, 50, 65), width=1 * scale
        )

        inner_x = content_x + (18 * scale)
        draw.text((inner_x, start_y + (12 * scale)), label.upper(), fill=(140, 150, 170), font=f_sub)
        draw.text((inner_x, start_y + (38 * scale)), f"{ping_val} MS", fill=(255, 255, 255), font=f_val)
        draw.text((content_x + panel_w - (130 * scale), start_y + (12 * scale)), status_str, fill=color, font=f_sub)

        bar_x, bar_y = inner_x, start_y + (68 * scale)
        bar_max_w = panel_w - (36 * scale)
        draw.rounded_rectangle([bar_x, bar_y, bar_x + bar_max_w, bar_y + (6 * scale)], radius=3 * scale, fill=(12, 14, 18))

        fill_w = int(min(1.0, ping_val / 500) * bar_max_w)
        if fill_w > 0:
            draw.rounded_rectangle([bar_x, bar_y, bar_x + fill_w, bar_y + (6 * scale)], radius=3 * scale, fill=color)

    draw_metric_block(155 * scale, "Gateway / WebSocket", ws_ping, ws_status, ws_color)
    draw_metric_block(255 * scale, "AI Inference Latency", groq_ping, groq_status, groq_color)

    footer_text = "AI System Metrics Visualizer"
    bbox = f_footer.getbbox(footer_text)
    footer_x = (card_w - (bbox[2] - bbox[0])) // 2
    draw.text((footer_x, card_h - (32 * scale)), footer_text, fill=(80, 90, 110), font=f_footer)

    buffer = io.BytesIO()
    base.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

def create_stats_card(avatar_bytes: bytes, uptime_str: str, requests: int, rate_limits: int, avg_latency: int) -> io.BytesIO:
    scale = 2
    card_w, card_h = 600 * scale, 450 * scale

    base = Image.new("RGBA", (card_w, card_h), (8, 10, 14, 255))
    overlay = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)

    overlay_draw.rounded_rectangle(
        [10 * scale, 10 * scale, card_w - (10 * scale), card_h - (10 * scale)],
        radius=16 * scale,
        fill=(14, 16, 22, 235),
        outline=(59, 130, 246),
        width=2 * scale
    )

    base = Image.alpha_composite(base, overlay)
    draw = ImageDraw.Draw(base)

    f_sub = get_font(12 * scale)
    f_title = get_font(24 * scale)
    f_val = get_font(16 * scale)
    f_footer = get_font(12 * scale)

    avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
    avatar_size = (100 * scale, 100 * scale)
    avatar = avatar.resize(avatar_size, Image.Resampling.LANCZOS)

    mask = Image.new("L", avatar_size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, avatar_size[0], avatar_size[1]), fill=255)
    base.paste(avatar, (35 * scale, 30 * scale), mask)

    draw.text((160 * scale, 42 * scale), "SYSTEM METRICS", fill=(140, 150, 170), font=f_sub)
    draw.text((160 * scale, 65 * scale), "BOT ANALYTICS", fill=(255, 255, 255), font=f_title)
    draw.line([35 * scale, 145 * scale, card_w - (35 * scale), 145 * scale], fill=(40, 45, 55), width=1 * scale)

    metrics = [
        ("UPTIME", uptime_str, (0, 240, 255)),
        ("REQUESTS SERVED", f"{requests} REQ", (255, 255, 255)),
        ("RATE LIMIT HITS", f"{rate_limits} HITS", (255, 170, 0) if rate_limits > 0 else (140, 150, 170)),
        ("AVG API LATENCY", f"{avg_latency} MS", (0, 240, 255) if avg_latency < 200 else (255, 60, 80))
    ]

    grid_y_start = 160 * scale
    for idx, (label, value, color) in enumerate(metrics):
        row = idx // 2
        col = idx % 2
        
        box_x = (35 + (col * 270)) * scale
        box_y = grid_y_start + (row * 105 * scale)
        box_w = 260 * scale
        box_h = 90 * scale

        draw.rounded_rectangle(
            [box_x, box_y, box_x + box_w, box_y + box_h],
            radius=10 * scale, fill=(20, 24, 32), outline=(45, 50, 65), width=1 * scale
        )

        draw.text((box_x + (15 * scale), box_y + (15 * scale)), label, fill=(140, 150, 170), font=f_sub)
        draw.text((box_x + (15 * scale), box_y + (45 * scale)), value, fill=color, font=f_val)

    footer_text = "AI System Metrics Visualizer"
    bbox = f_footer.getbbox(footer_text)
    footer_x = (card_w - (bbox[2] - bbox[0])) // 2
    draw.text((footer_x, card_h - (32 * scale)), footer_text, fill=(80, 90, 110), font=f_footer)

    buffer = io.BytesIO()
    base.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

def create_usercard(avatar_bytes: bytes, username: str, joined_at: str, created_at: str, top_role: str) -> io.BytesIO:
    scale = 2
    card_w, card_h = 600 * scale, 320 * scale

    base = Image.new("RGBA", (card_w, card_h), (8, 10, 14, 255))
    draw = ImageDraw.Draw(base)

    draw.rounded_rectangle(
        [10 * scale, 10 * scale, card_w - (10 * scale), card_h - (10 * scale)],
        radius=16 * scale, fill=(14, 16, 22, 235), outline=(59, 130, 246), width=2 * scale
    )

    f_sub = get_font(11 * scale)
    f_title = get_font(22 * scale)
    f_val = get_font(13 * scale)

    avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
    avatar_size = (100 * scale, 100 * scale)
    avatar = avatar.resize(avatar_size, Image.Resampling.LANCZOS)

    mask = Image.new("L", avatar_size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, avatar_size[0], avatar_size[1]), fill=255)
    base.paste(avatar, (30 * scale, 30 * scale), mask)

    draw.text((150 * scale, 35 * scale), "USER PROFILE", fill=(59, 130, 246), font=f_sub)
    draw.text((150 * scale, 55 * scale), username[:18].upper(), fill=(255, 255, 255), font=f_title)
    draw.line([30 * scale, 145 * scale, card_w - (30 * scale), 145 * scale], fill=(40, 45, 55), width=1 * scale)

    fields = [
        ("JOIN DATE", joined_at),
        ("ACCOUNT CREATED", created_at),
        ("TOP ROLE", top_role)
    ]

    for idx, (label, val) in enumerate(fields):
        y_pos = (160 + (idx * 45)) * scale
        draw.text((35 * scale, y_pos), label, fill=(120, 130, 150), font=f_sub)
        draw.text((180 * scale, y_pos), val, fill=(240, 240, 240), font=f_val)

    buffer = io.BytesIO()
    base.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer
