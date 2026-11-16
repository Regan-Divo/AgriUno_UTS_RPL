"""
==========================================================
PEMBANGUN DIAGRAM - AGRIUNO (UAS RPL 2026)
==========================================================
Skrip ini membangkitkan seluruh berkas diagram ``.drawio`` yang
digunakan pada laporan AgriUno. Setiap diagram dibangun dari data
yang bersumber langsung pada kode sumber aplikasi, sehingga isi
diagram, tabel laporan, dan implementasi kode selalu selaras.

Daftar diagram yang dibangkitkan:

  03_Diagram_Konteks.drawio              Diagram Konteks (Level 0)
  03_DFD_Level_1.drawio                  DFD Level 1
  03_DFD_L2_Proses_1_0.drawio             DFD Level 2 - Proses 1.0
  03_DFD_L2_Proses_2_0.drawio             DFD Level 2 - Proses 2.0
  03_DFD_L2_Proses_3_0.drawio             DFD Level 2 - Proses 3.0
  03_DFD_L2_Proses_4_0.drawio             DFD Level 2 - Proses 4.0
  04_Use_Case_Diagram.drawio              Use Case Diagram
  04_Sequence_Diagram_UC-01_Login.drawio  Sequence Diagram UC-01
  04_Sequence_Diagram_UC-03_Petani.drawio Sequence Diagram UC-03
  04_Sequence_Diagram_UC-04_Panen.drawio  Sequence Diagram UC-04
  04_Sequence_Diagram_UC-05_Distribusi.drawio Sequence Diagram UC-05
  04_Sequence_Diagram_UC-08_Registrasi.drawio Sequence Diagram UC-08
  04_Activity_Diagram.drawio              Activity Diagram
  04_Activity_Diagram_Splash.drawio       Activity Diagram alur splash
  04_Class_Diagram.drawio                 Class Diagram
  05_Entity_Relationship_Diagram.drawio   ERD
  06_Arsitektur_Sistem.drawio             Arsitektur Sistem
  06_Diagram_Navigasi.drawio              Diagram Navigasi

Jalankan::

    python tools/generate_diagrams.py

Hasilnya dapat diekspor menjadi PNG menggunakan draw.io desktop::

    draw.io --export --format png --scale 2 --output <file>.png <file>.drawio
"""

import os
from xml.sax.saxutils import escape

# ============================================================
# KONSTANTA WARNA (selaras dengan config/constants.py)
# ============================================================
HIJAU_TUA = "#1b4332"
HIJAU_TENGAH = "#2d6a4f"
HIJAU_MUDA = "#95c5a0"
BIRU = "#1d4ed8"
ORANYE = "#d97706"
MERAH = "#dc2626"
TOSKA = "#0f766e"

TEKS = "#1f2937"
TEKS_MUTED = "#6b7280"
TEKS_PUTIH = "#ffffff"
GARIS = "#d1d5db"
LATAR = "#ffffff"
LATAR_PROSES = "#f2f9f5"
LATAR_ENTITAS = "#f7fbf8"
LATAR_SISTEM = "#eef4ff"

# ============================================================
# GAYA (style) mxGraph
# ============================================================
S_JUDUL = (
    "text;html=1;whiteSpace=wrap;rounded=0;strokeColor=none;fillColor=none;"
    "align=center;verticalAlign=top;fontSize=25;fontStyle=1;fontColor=%s;spacing=2;" % HIJAU_TUA
)
S_SUBJUDUL = (
    "text;html=1;whiteSpace=wrap;rounded=0;strokeColor=none;fillColor=none;"
    "align=center;verticalAlign=top;fontSize=15;fontColor=%s;spacing=2;" % TEKS_MUTED
)
S_CATATAN = (
    "text;html=1;whiteSpace=wrap;rounded=0;strokeColor=none;fillColor=none;"
    "align=left;verticalAlign=top;fontSize=14;fontColor=%s;spacing=2;" % TEKS_MUTED
)
S_LABEL = (
    "text;html=1;whiteSpace=wrap;rounded=0;strokeColor=none;fillColor=none;"
    "align=center;verticalAlign=top;fontSize=14;fontStyle=1;fontColor=%s;spacing=2;" % HIJAU_TUA
)
S_ENTITAS = (
    "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;strokeWidth=1.4;"
    "fontSize=17;fontStyle=1;fontColor=%s;align=center;verticalAlign=middle;"
    "spacing=8;spacingLineHeight=100%%;arcSize=0;" % (LATAR_ENTITAS, HIJAU_MUDA, TEKS)
)
S_AKTOR = (
    "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;strokeWidth=1.4;"
    "fontSize=17;fontStyle=1;fontColor=%s;align=center;verticalAlign=middle;"
    "spacing=8;spacingLineHeight=100%%;arcSize=0;" % (LATAR_SISTEM, "#a5b4fc", TEKS)
)
S_PROSES = (
    "rounded=1;arcSize=8;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=#4b5563;"
    "strokeWidth=1.6;verticalAlign=top;align=center;spacingTop=8;fontSize=17;"
    "fontStyle=1;fontColor=%s;" % (LATAR_PROSES, TEKS)
)
S_NAMA_PROSES = (
    "text;html=1;whiteSpace=wrap;rounded=0;strokeColor=none;fillColor=none;"
    "align=center;verticalAlign=middle;fontSize=15;fontColor=%s;spacing=2;" % TEKS
)
S_STORE = (
    "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;strokeWidth=1.6;"
    "fontSize=15;fontColor=%s;align=center;verticalAlign=middle;" % (LATAR, HIJAU_TUA, TEKS)
)
S_STORE_TERBUKA = (
    "rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=%s;strokeWidth=1.6;"
    "fontSize=15;fontColor=%s;align=center;verticalAlign=middle;" % (HIJAU_TUA, TEKS)
)
S_USECASE = (
    "ellipse;whiteSpace=wrap;html=1;fillColor=#e8f5ee;strokeColor=%s;strokeWidth=1.5;"
    "fontSize=15;fontColor=%s;align=center;verticalAlign=middle;" % (HIJAU_TUA, TEKS)
)
S_SISTEM = (
    "rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=%s;strokeWidth=1.8;"
    "fontSize=14;fontColor=%s;align=center;verticalAlign=middle;" % (HIJAU_TUA, TEKS)
)
S_HEADER = (
    "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;strokeWidth=1.8;"
    "fontSize=15;fontStyle=1;fontColor=%s;align=center;verticalAlign=middle;"
    % (HIJAU_TUA, HIJAU_TUA, TEKS_PUTIH)
)
S_BOX = (
    "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;strokeWidth=1.2;"
    "fontSize=14;fontColor=%s;align=left;verticalAlign=middle;spacingLeft=10;"
    % (LATAR, GARIS, TEKS)
)
S_BOX_HEADER = (
    "rounded=0;whiteSpace=wrap;html=1;fillColor=#eef5f0;strokeColor=%s;strokeWidth=1.2;"
    "fontSize=14;fontStyle=1;fontColor=%s;align=left;verticalAlign=middle;spacingLeft=10;"
    % (HIJAU_MUDA, HIJAU_TUA)
)
S_CLASS_HEADER = (
    "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;strokeWidth=1.6;"
    "fontSize=15;fontStyle=1;fontColor=%s;align=center;verticalAlign=middle;"
    % (HIJAU_TUA, HIJAU_TUA, TEKS_PUTIH)
)
S_CLASS_BODY = (
    "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;strokeWidth=1.6;"
    "fontSize=13;fontColor=%s;align=center;verticalAlign=middle;" % (LATAR, HIJAU_TUA, TEKS)
)
S_CLASS_FILE = (
    "text;html=1;whiteSpace=wrap;rounded=0;strokeColor=none;fillColor=none;"
    "align=center;verticalAlign=top;fontSize=11;fontStyle=2;fontColor=%s;spacing=2;" % TEKS_MUTED
)
S_LIFELINE = (
    "rounded=0;whiteSpace=wrap;html=1;fillColor=#e8f5ee;strokeColor=%s;strokeWidth=1.4;"
    "fontSize=14;fontStyle=1;fontColor=%s;align=center;verticalAlign=middle;" % (HIJAU_TUA, TEKS)
)
S_LIFELINE_SUB = (
    "text;html=1;whiteSpace=wrap;rounded=0;strokeColor=none;fillColor=none;"
    "align=center;verticalAlign=top;fontSize=11;fontStyle=2;fontColor=%s;spacing=2;" % TEKS_MUTED
)
S_MSG = (
    "text;html=1;whiteSpace=wrap;rounded=0;strokeColor=none;fillColor=none;"
    "align=left;verticalAlign=middle;fontSize=13;fontColor=%s;spacing=2;" % TEKS
)
S_ACTIVITAS = (
    "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;strokeWidth=1.4;"
    "fontSize=14;fontColor=%s;align=center;verticalAlign=middle;spacing=8;"
    % (LATAR, HIJAU_MUDA, TEKS)
)
S_KEPUTUSAN = (
    "rhombus;whiteSpace=wrap;html=1;fillColor=#fff7ed;strokeColor=%s;strokeWidth=1.4;"
    "fontSize=13;fontColor=%s;align=center;verticalAlign=middle;" % (ORANYE, TEKS)
)
S_AWAL = (
    "ellipse;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;strokeWidth=1.4;"
    "fontSize=13;fontColor=%s;alig"
    "n=center;verticalAlign=middle;" % (HIJAU_TUA, HIJAU_TUA, TEKS_PUTIH)
)
S_AKHIR = (
    "ellipse;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;strokeWidth=1.4;"
    "fontSize=13;fontColor=%s;align=center;verticalAlign=middle;" % (LATAR, HIJAU_TUA, TEKS)
)
S_ERROR = (
    "rounded=0;whiteSpace=wrap;html=1;fillColor=#fef2f2;strokeColor=%s;strokeWidth=1.4;"
    "fontSize=13;fontColor=#991b1b;align=center;verticalAlign=middle;spacing=8;" % MERAH
)
S_SWIMLANE = (
    "rounded=0;whiteSpace=wrap;html=1;fillColor=#fbfdfc;strokeColor=%s;strokeWidth=1.2;"
    "fontSize=13;fontColor=%s;align=center;verticalAlign=middle;" % (GARIS, TEKS)
)
S_SWIMLANE_HEADER = (
    "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;strokeWidth=1.2;"
    "fontSize=14;fontStyle=1;fontColor=%s;align=center;verticalAlign=middle;"
    % (HIJAU_TUA, HIJAU_TUA, TEKS_PUTIH)
)


def S_EDGE(label="", dashed=False, color=TEKS, width=1.4, arrow="block", extra=""):
    """Membangun gaya garis aliran data."""
    parts = [
        "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;",
        "strokeColor=%s;strokeWidth=%s;" % (color, width),
        "endArrow=%s;endFill=1;" % arrow,
        "dashed=%s;" % ("1" if dashed else "0"),
        "labelBackgroundColor=#ffffff;fontSize=13;fontColor=%s;" % TEKS,
        "labelBorderColor=#FFFFFF;spacing=3;",
    ]
    if extra:
        parts.append(extra)
    return "".join(parts)


S_EDGE_PLAIN = (
    "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=%s;strokeWidth=1.4;"
    "endArrow=none;dashed=0;" % TEKS
)
S_LINE = "endArrow=none;html=1;rounded=0;strokeColor=%s;strokeWidth=1.2;dashed=0;" % GARIS


# ============================================================
# KELAS PEMBANGUN DIAGRAM
# ============================================================
class Diagram:
    """Pembangun berkas mxGraph (draw.io) yang sederhana."""

    def __init__(self, name, width=1400, height=800, page_name=None):
        self.name = name
        self.page_name = page_name or name
        self.width = width
        self.height = height
        self.cells = []
        self._counter = 0

    # --------------------------------------------------------
    def _next_id(self, prefix):
        self._counter += 1
        return "%s_%d" % (prefix, self._counter)

    # --------------------------------------------------------
    def node(self, value, style, x, y, w, h, node_id=None):
        """Menambahkan simpul (node) ke diagram."""
        node_id = node_id or self._next_id("n")
        self.cells.append(
            '        <mxCell id="%s" value="%s" style="%s" vertex="1" parent="1">'
            '<mxGeometry x="%s" y="%s" width="%s" height="%s" as="geometry"/></mxCell>'
            % (node_id, escape(str(value)), style, x, y, w, h)
        )
        return node_id

    # --------------------------------------------------------
    def text(self, value, x, y, w, h, style=S_CATATAN, node_id=None):
        """Menambahkan label teks bebas."""
        return self.node(value, style, x, y, w, h, node_id)

    # --------------------------------------------------------
    def edge(
        self,
        source,
        target,
        value="",
        style=None,
        points=None,
        edge_id=None,
        exit_xy=None,
        entry_xy=None,
        label_offset=None,
    ):
        """Menambahkan garis penghubung antar simpul.

        ``exit_xy`` dan ``entry_xy`` berupa pasangan (rasio_x, rasio_y)
        yang menentukan titik keluar dan masuk pada sisi kotak sumber
        dan target. Parameter ini dipakai untuk mencegah label aliran
        data saling bertumpuk.

        ``label_offset`` berupa pasangan (dx, dy) yang menggeser
        label aliran data dari posisi tengah lintasan.
        """
        edge_id = edge_id or self._next_id("e")
        style = style if style is not None else S_EDGE(value)

        if exit_xy is not None:
            style += "exitX=%s;exitY=%s;exitDx=0;exitDy=0;" % (exit_xy[0], exit_xy[1])
        if entry_xy is not None:
            style += "entryX=%s;entryY=%s;entryDx=0;entryDy=0;" % (entry_xy[0], entry_xy[1])

        geo = '<mxGeometry relative="1" as="geometry">'
        if points:
            geo += '<Array as="points">'
            for px, py in points:
                geo += '<mxPoint x="%s" y="%s"/>' % (px, py)
            geo += "</Array>"
        if label_offset is not None:
            geo += '<mxPoint x="%s" y="%s" as="offset"/>' % (label_offset[0], label_offset[1])
        geo += "</mxGeometry>"
        self.cells.append(
            '        <mxCell id="%s" value="%s" style="%s" edge="1" parent="1" '
            'source="%s" target="%s">%s</mxCell>'
            % (edge_id, escape(str(value)), style, source, target, geo)
        )
        return edge_id

    # --------------------------------------------------------
    def line(self, x1, y1, x2, y2, style=S_LINE, edge_id=None):
        """Menambahkan garis lurus bebas (tanpa sumber/tujuan)."""
        edge_id = edge_id or self._next_id("l")
        self.cells.append(
            '        <mxCell id="%s" style="%s" edge="1" parent="1">'
            '<mxGeometry relative="1" as="geometry">'
            '<mxPoint x="%s" y="%s" as="sourcePoint"/>'
            '<mxPoint x="%s" y="%s" as="targetPoint"/></mxGeometry></mxCell>'
            % (edge_id, style, x1, y1, x2, y2)
        )
        return edge_id

    # --------------------------------------------------------
    def to_xml(self):
        """Menyusun keluaran XML lengkap berkas .drawio."""
        body = "\n".join(self.cells)
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<mxfile host="app.diagrams.net" agent="AgriUno-Dokumentasi-UAS-RPL" '
            'version="24.7.17" type="device">\n'
            '  <diagram id="agriuno-uas" name="%s">\n'
            '    <mxGraphModel dx="1400" dy="800" grid="1" gridSize="10" '
            'guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" '
            'pageScale="1" pageWidth="%s" pageHeight="%s" math="0" shadow="0">\n'
            "      <root>\n"
            '        <mxCell id="0"/>\n'
            '        <mxCell id="1" parent="0"/>\n'
            "%s\n"
            "      </root>\n"
            "    </mxGraphModel>\n"
            "  </diagram>\n"
            "</mxfile>\n" % (escape(self.page_name), self.width, self.height, body)
        )

    # --------------------------------------------------------
    def save(self, path):
        """Menulis diagram ke berkas .drawio."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(self.to_xml())
        return path


# ============================================================
# HELPER UML
# ============================================================
def lifeline(diag, x, name, subtitle, y=80, w=210, h=34):
    """Menyusun lifeline untuk sequence diagram."""
    head = diag.node("", S_LIFELINE, x, y, w, h)
    diag.text(name, x, y + 2, w, h - 4, S_LIFELINE_SUB)
    diag.text(subtitle, x, y + h + 2, w, 16, S_LIFELINE_SUB)
    return head


def message(diag, x, y, w, text, align="left"):
    """Menyusun label pesan pada sequence diagram."""
    style = S_MSG
    if align == "center":
        style = S_MSG.replace("align=left", "align=center")
    return diag.text(text, x, y, w, 22, style)


def arrow(diag, x1, x2, y, color=TEKS, dashed=False, arrow_type="block"):
    """Menyusun garis panah horizontal pada sequence diagram."""
    style = "endArrow=%s;html=1;rounded=0;strokeColor=%s;strokeWidth=1.4;dashed=%s;" % (
        arrow_type,
        color,
        "1" if dashed else "0",
    )
    return diag.line(x1, y, x2, y, style)


def arrow_v(diag, x, y1, y2, color=TEKS, dashed=False, arrow_type="block"):
    """Menyusun garis panah vertikal pada activity diagram."""
    style = "endArrow=%s;html=1;rounded=0;strokeColor=%s;strokeWidth=1.4;dashed=%s;" % (
        arrow_type,
        color,
        "1" if dashed else "0",
    )
    return diag.line(x, y1, x, y2, style)


def arrow_h(diag, y, x1, x2, color=TEKS, dashed=False, arrow_type="block"):
    """Menyusun garis panah horizontal pada activity diagram."""
    style = "endArrow=%s;html=1;rounded=0;strokeColor=%s;strokeWidth=1.4;dashed=%s;" % (
        arrow_type,
        color,
        "1" if dashed else "0",
    )
    return diag.line(x1, y, x2, y, style)


def uml_class(diag, x, y, w, name, file_name, attributes, methods, h=None):
    """Menyusun satu kelas pada class diagram.

    Mengembalikan dict berisi id simpul dan koordinat untuk keperluan
    penyusunan garis relasi.
    """
    attr_h = 22 * max(1, len(attributes))
    meth_h = 22 * max(1, len(methods))
    total_h = h or (40 + attr_h + meth_h + 12)

    diag.node("", S_CLASS_HEADER, x, y, w, 40)
    diag.text(
        name,
        x,
        y + 2,
        w,
        24,
        S_CLASS_HEADER.replace("fillColor=%s" % HIJAU_TUA, "fillColor=%s" % HIJAU_TUA),
    )
    diag.text(file_name, x, y + 24, w, 14, S_CLASS_FILE)

    diag.node("", S_CLASS_BODY, x, y, w, total_h)
    diag.line(x, y + 40, x + w, y + 40, S_LINE)
    diag.line(x, y + 40 + attr_h, x + w, y + 40 + attr_h, S_LINE)

    diag.text(
        "<br>".join(attributes) if attributes else "",
        x + 8,
        y + 44,
        w - 16,
        attr_h,
        S_MSG.replace("align=left", "align=left").replace("fontSize=13", "fontSize=12"),
    )
    diag.text(
        "<br>".join(methods) if methods else "",
        x + 8,
        y + 44 + attr_h,
        w - 16,
        meth_h,
        S_MSG.replace("fontSize=13", "fontSize=12"),
    )

    return {"x": x, "y": y, "w": w, "h": total_h}
