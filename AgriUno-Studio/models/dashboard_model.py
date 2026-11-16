"""Model rekapitulasi angka untuk kartu KPI Dashboard."""

import logging
from decimal import Decimal

from config.database import DatabaseTidakTersedia, kursor
from AgriUno_UTS_RPL.models.base_model import ke_decimal

logger = logging.getLogger(__name__)


class DashboardModel:
    """Model rekapitulasi angka Dashboard."""

    @staticmethod
    def get_statistik():
        """Ringkasan angka untuk kartu KPI Dashboard."""
        data = {
            "total_petani": 0,
            "total_lot": 0,
            "total_alokasi": 0,
            "total_setor": Decimal("0"),
            "total_kirim": Decimal("0"),
            "petani_aktif": 0,
            "komoditas": [],
            "aktivitas": [],
        }
        try:
            with kursor(commit=False) as cur:
                cur.execute("SELECT COUNT(*) AS t FROM petani")
                data["total_petani"] = int(cur.fetchone()["t"])
                cur.execute("SELECT COUNT(*) AS t FROM inventori_panen")
                data["total_lot"] = int(cur.fetchone()["t"])
                cur.execute("SELECT COUNT(*) AS t FROM distribusi")
                data["total_alokasi"] = int(cur.fetchone()["t"])
                cur.execute("SELECT COALESCE(SUM(jumlah_berat), 0) AS t FROM inventori_panen")
                data["total_setor"] = ke_decimal(cur.fetchone()["t"])
                cur.execute("SELECT COALESCE(SUM(jumlah_dikirim), 0) AS t FROM distribusi")
                data["total_kirim"] = ke_decimal(cur.fetchone()["t"])
                cur.execute(
                    "SELECT COUNT(DISTINCT p.id_petani) AS t FROM petani p "
                    "INNER JOIN inventori_panen ip ON ip.id_petani = p.id_petani"
                )
                data["petani_aktif"] = int(cur.fetchone()["t"])
                cur.execute(
                    "SELECT jenis_komoditas, SUM(jumlah_berat) AS berat "
                    "FROM inventori_panen GROUP BY jenis_komoditas "
                    "ORDER BY berat DESC LIMIT 3"
                )
                data["komoditas"] = cur.fetchall()
                cur.execute(
                    "SELECT 'panen' AS jenis, ip.id_panen AS id, ip.tgl_panen AS tgl, "
                    "ip.jenis_komoditas AS keterangan, ip.jumlah_berat AS berat, '' AS status, "
                    "pt.nama_petani FROM inventori_panen ip LEFT JOIN petani pt "
                    "ON pt.id_petani = ip.id_petani "
                    "UNION ALL "
                    "SELECT 'distribusi' AS jenis, d.id_distribusi AS id, ip.tgl_panen AS tgl, "
                    "d.tujuan_pengiriman AS keterangan, d.jumlah_dikirim AS berat, "
                    "d.status_pengiriman AS status, pt.nama_petani "
                    "FROM distribusi d LEFT JOIN inventori_panen ip ON ip.id_panen = d.id_panen "
                    "LEFT JOIN petani pt ON pt.id_petani = ip.id_petani "
                    "ORDER BY tgl DESC, id DESC LIMIT 7"
                )
                data["aktivitas"] = cur.fetchall()
        except DatabaseTidakTersedia as exc:
            logger.error("statistik: %s", exc)
        return data
