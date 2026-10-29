from app import db
from app.models import Acompanhamento, Ocorrencia, Pedido


def test_painel_exibe_dados_demo(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Cliente Exemplo A" in response.data
    assert b"Cliente Exemplo B" in response.data


def test_pesquisa_por_regiao_e_canal(client):
    response = client.get("/?regiao=Norte&canal=Marketplace")
    assert b"Cliente Exemplo B" in response.data
    assert b"Cliente Exemplo A" not in response.data


def test_cadastro_valido_persiste_pedido_e_acompanhamento(client, app):
    response = client.post(
        "/pedidos/novo",
        data={
            "destinatario": "Cliente de Teste",
            "destino": "Rua de Teste, 10",
            "regiao": "Leste",
            "canal_venda": "Loja física",
            "descricao_volume": "Pacote pequeno",
            "status": "Pendente",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Cliente de Teste" in response.data
    with app.app_context():
        pedido = Pedido.query.filter_by(destinatario="Cliente de Teste").one()
        assert pedido.identificador == "1004"
        assert len(pedido.acompanhamentos) == 1


def test_cadastro_invalido_rejeita_status(client):
    response = client.post(
        "/pedidos/novo",
        data={
            "destinatario": "Cliente Inválido",
            "destino": "Rua",
            "regiao": "Centro",
            "canal_venda": "Loja virtual",
            "descricao_volume": "Pacote",
            "status": "Status inventado",
        },
    )
    assert response.status_code == 200
    assert b"status informado n\xc3\xa3o \xc3\xa9 permitido" in response.data


def test_atualizacao_preserva_historico(client, app):
    response = client.post(
        "/pedidos/1001/status",
        data={"status": "Entregue", "observacao": "Entrega confirmada."},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Entrega confirmada." in response.data
    with app.app_context():
        pedido = Pedido.query.filter_by(identificador="1001").one()
        assert pedido.status == "Entregue"
        assert len(pedido.acompanhamentos) == 3


def test_registra_e_consulta_ocorrencia(client, app):
    response = client.post(
        "/pedidos/1001/ocorrencias",
        data={
            "tipo": "Atraso",
            "descricao": "Chuva afetou a rota.",
            "providencia": "Reprogramar entrega.",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Chuva afetou a rota." in response.data
    with app.app_context():
        ocorrencia = Ocorrencia.query.filter_by(tipo="Atraso").one()
        assert ocorrencia.pedido.identificador == "1001"


def test_integridade_dos_relacionamentos(app):
    with app.app_context():
        pedido = Pedido.query.filter_by(identificador="1003").one()
        assert pedido.regiao.nome == "Sul"
        assert all(item.pedido_id == pedido.id for item in pedido.ocorrencias)
        assert all(item.pedido_id == pedido.id for item in pedido.acompanhamentos)
        assert db.session.get(Acompanhamento, pedido.acompanhamentos[0].id).pedido is pedido
