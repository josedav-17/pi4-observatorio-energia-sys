from datetime import date
from unittest.mock import Mock

from src.extract import xm, xm_aportes
from src.utils import ventanas


def test_ventanas_cubre_el_rango_sin_solapamientos():
    resultado = list(ventanas(date(2026, 1, 1), date(2026, 2, 2), 30))

    assert resultado == [
        (date(2026, 1, 1), date(2026, 1, 30)),
        (date(2026, 1, 31), date(2026, 2, 2)),
    ]


def test_aplanar_interpreta_list_entities():
    respuesta = {
        "Items": [
            {
                "Date": "2026-10-24",
                "ListEntities": [
                    {"Id": "Sistema", "Values": {"Code": "2QBW", "Name": "EL POPAL"}}
                ],
            }
        ]
    }

    assert xm.aplanar(respuesta, "lists") == [
        {"Date": "2026-10-24", "Id": "Sistema", "Code": "2QBW", "Name": "EL POPAL"}
    ]


def test_aportes_omite_archivo_existente(monkeypatch):
    ya_existe = Mock(return_value=True)
    peticion = Mock(side_effect=AssertionError("No debe consultar la API"))
    monkeypatch.setattr(xm_aportes, "ya_existe", ya_existe)
    monkeypatch.setattr(xm_aportes, "http_json", peticion)

    xm_aportes.extraer()

    ya_existe.assert_called_once_with("xm_aportes_hidricos", False)
    peticion.assert_not_called()


def test_ideam_temperatura_agrega_en_soql():
    from src.extract.ideam_temperatura import consulta_soql

    consulta = consulta_soql(date(2025, 1, 1), date(2025, 1, 7), 0)

    assert "avg(valorobservado)" in consulta["$select"]
    assert "min(valorobservado)" in consulta["$select"]
    assert "max(valorobservado)" in consulta["$select"]
    assert "date_trunc_ymd(fechaobservacion)" in consulta["$select"]
    assert "departamento = 'ANTIOQUIA'" in consulta["$where"]
    assert consulta["$limit"] == 50000
