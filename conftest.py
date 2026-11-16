"""
==========================================================
KONFIGURASI PENGUJIAN (conftest) - AGRIUNO
==========================================================
Menyediakan fixture bersama untuk seluruh pengujian pada folder
``tests/``.

Fixture ``_skip_when_database_unavailable`` dipakai oleh pengujian
yang ditandai ``@pytest.mark.db`` (baik pada ``test_model.py`` di root
maupun berkas di folder ``tests/``). Pengujian tersebut otomatis
dilewati (skip) apabila server MySQL tidak dapat dihubungi,
sehingga pipeline CI pada GitHub Actions tetap berjalan hijau
meskipun runner tidak menyediakan MySQL.

Untuk menjalankan pengujian yang memerlukan basis data:

    pytest -v -m db

Pastikan layanan MySQL pada Laragon sedang aktif dan skrip
``database.sql`` sudah pernah dijalankan.
"""

import pytest

from config.database import DatabaseConnection


@pytest.fixture(scope="session")
def database_tersedia():
    """Menyatakan apakah server MySQL dapat dihubungi."""
    try:
        return DatabaseConnection.ping()
    except Exception:  # noqa: BLE001 - jaring pengaman pengujian
        return False


@pytest.fixture(autouse=True)
def _skip_when_database_unavailable(request, database_tersedia):
    """Melewati pengujian bertanda ``db`` bila MySQL tidak tersedia."""
    if request.node.get_closest_marker("db") is None:
        return
    if not database_tersedia:
        pytest.skip(
            "Server MySQL tidak dapat dihubungi. Jalankan 'pytest -m db' dengan MySQL aktif."
        )
