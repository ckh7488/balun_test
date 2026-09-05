"""Export native KiCad PCB layers plus a current schematic for visual review."""
import io
from pathlib import Path
import subprocess

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
STAGE = ROOT / "outputs/balun-llc16-pcb-20260903/stage"
OUTPUT = ROOT / "output/pdf"
CLI = "C:/Program Files/KiCad/10.0/bin/kicad-cli.exe"


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    writer = PdfWriter()
    pages = [
        ("top", "F.Cu,F.Silkscreen,Edge.Cuts", False, "TOP / RF AND DIFFERENTIAL ROUTES",
         "All signal routes on F.Cu; no signal vias. J1 is mounted on the opposite side."),
        ("bottom", "B.Cu,B.Silkscreen,Edge.Cuts", True, "BOTTOM / COMPONENT-SIDE VIEW",
         "J1: male M12, MB12MBAFF08ST-3. PG9 panel support required. RCT1/RCT2 remain DNP."),
        ("inner1", "In1.Cu,Edge.Cuts", False, "L2 / GND REFERENCE BELOW SIGNALS",
         "Filled /GND plane; pad and drill clearances retained. No inner-layer signal routes."),
        ("inner2", "In2.Cu,Edge.Cuts", False, "L3 / SECOND GND PLANE",
         "Filled /GND plane. M12 pins 1/5/6/7 have no trace or plane connection."),
    ]
    for index, (name, layers, mirror, heading, note) in enumerate(pages, 1):
        path = STAGE / f"{name}.pdf"
        command = [CLI, "pcb", "export", "pdf", "--mode-single", "--layers", layers,
                   "--scale", "3", "--bg-color", "#22303c", "-o", str(path), str(STAGE / "balun_llc16.kicad_pcb")]
        if mirror:
            command.append("--mirror")
        subprocess.run(command, check=True)
        page = PdfReader(path).pages[0]
        width, height = float(page.mediabox.width), float(page.mediabox.height)
        overlay = io.BytesIO()
        c = canvas.Canvas(overlay, pagesize=(width, height))
        c.setFillColor(HexColor("#f5f7fa"))
        c.setFont("Helvetica-Bold", 16)
        c.drawString(34, height-32, "LLC / ACTUATOR to RJ45")
        c.setFont("Helvetica", 10)
        c.drawString(34, height-49, heading)
        c.setFont("Helvetica-Bold", 10)
        c.drawRightString(width-34, height-32, "PCB DRAFT A | DO NOT ORDER")
        c.setFont("Helvetica", 9)
        c.drawString(34, 35, note)
        c.drawString(34, 21, "68 x 44 mm | 4 layers | JLC04161H-7628 | 50R W0.35 / 100R W0.23 G0.22 | Native CAD plot, 3:1")
        c.drawRightString(width-34, 21, f"{index} / 4")
        c.save()
        page.merge_page(PdfReader(overlay).pages[0])
        writer.add_page(page)
    writer.add_metadata({"/Title": "LLC VNA Fixture - PCB DRAFT A", "/Subject": "Review only; not a fabrication release"})
    writer.write(OUTPUT / "balun_llc16_pcb_review.pdf")
    subprocess.run([CLI, "sch", "export", "pdf", "--no-background-color", "--exclude-pdf-property-popups", "-o",
                    str(OUTPUT / "balun_llc16_schematic.pdf"), str(STAGE / "balun_llc16.kicad_sch")], check=True)


if __name__ == "__main__":
    main()
