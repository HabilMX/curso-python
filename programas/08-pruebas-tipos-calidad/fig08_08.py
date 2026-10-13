# fig08_08.py
import pytest

UMBRAL_LENTO_MS = 1000


def es_lento(tiempo_ms: int) -> bool:
    return tiempo_ms >= UMBRAL_LENTO_MS


def test_con_el_umbral_normal() -> None:
    assert es_lento(1500)


def test_con_un_umbral_mas_alto(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("fig08_08.UMBRAL_LENTO_MS", 3000)
    assert not es_lento(1500)


def test_el_umbral_vuelve_a_su_valor() -> None:
    assert UMBRAL_LENTO_MS == 1000
