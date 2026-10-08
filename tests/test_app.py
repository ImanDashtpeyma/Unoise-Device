import app as app_module

flask_app = app_module.app


def make_client():
    flask_app.config["TESTING"] = True
    return flask_app.test_client()


def test_chart_without_data_returns_404():
    app_module.sound_data.clear()
    response = make_client().get("/chart")
    assert response.status_code == 404


def test_receive_data_rejects_invalid_payload():
    response = make_client().post("/receive_data", json={"foo": "bar"})
    assert response.status_code == 400


def test_predict_rejects_invalid_payload():
    response = make_client().post("/predict", json={"foo": "bar"})
    assert response.status_code == 400


def test_predict_returns_a_known_label():
    response = make_client().post("/predict", json={"decibels": 70})
    assert response.status_code == 200
    assert response.get_json()["prediction"] in app_module.LABEL_MAP.values()


def test_receive_data_stores_entry_with_prediction(monkeypatch):
    # Do not write to the CSV file during tests
    monkeypatch.setattr(app_module, "save_to_csv", lambda entry: None)
    app_module.sound_data.clear()

    response = make_client().post(
        "/receive_data", json={"sound": "loud", "decibels": 72.5}
    )

    assert response.status_code == 200
    entry = response.get_json()["entry"]
    assert entry["decibels"] == 72.5
    assert entry["prediction"] in app_module.LABEL_MAP.values()
    assert len(app_module.sound_data) == 1
