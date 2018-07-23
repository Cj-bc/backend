import pytest

from utils import (
    login,
    admin,
    test_user,
    as_user_get,
    invalid_classroom_id,
    invalid_lottery_id,
    make_application
)

from api.models import Lottery, Classroom, User, Application, db
from api.schemas import (
    user_schema,
    classrooms_schema,
    classroom_schema,
    application_schema,
    applications_schema,
    lotteries_schema,
    lottery_schema
)


# ---------- Lottery API

@pytest.mark.classrooms
@pytest.mark.all
def test_get_allclassrooms(client):
    """test proper infomation is returned from the API
        target_url: /classrooms
    """
    resp = client.get('/classrooms')

    with client.application.app_context():
        db_status = Classroom.query.all()
        classroom_list = classrooms_schema.dump(db_status)[0]

    assert resp.get_json() == classroom_list


def test_get_specific_classroom(client):
    """test proper infomation is returned from the API
        target_url: /classrooms/<id>
    """
    idx = '1'  # classroom id to test
    resp = client.get('/classrooms/'+idx)

    with client.application.app_context():
        db_status = Classroom.query.filter_by(id=idx).first()
        classroom = classroom_schema.dump(db_status)[0]

    assert resp.get_json() == classroom


def test_get_specific_classroom_invaild_id(client):
    """test proper errpr is returned from the API
        target_url: /classrooms/<id>
    """
    idx = invalid_classroom_id  # classroom id to test
    resp = client.get('/classrooms/'+idx)

    assert resp.status_code == 404
    assert 'Classroom could not be found.' in resp.get_json()['message']


def test_get_alllotteries(client):
    """test proper infomation is returned from the API
        target_url: /lotteries
    """
    resp = client.get('/lotteries')

    with client.application.app_context():
        db_status = Lottery.query.all()
        lottery_list = lotteries_schema.dump(db_status)[0]

    assert resp.get_json() == lottery_list


def test_get_specific_lottery(client):
    """test proper infomation is returned from the API
        target_url: /lotteries/<id>
    """
    idx = '1'  # lottery id to test
    resp = client.get('/lotteries/'+idx)

    with client.application.app_context():
        db_status = Lottery.query.filter_by(id=idx).first()
        lottery = lottery_schema.dump(db_status)[0]

    assert resp.get_json() == lottery


def test_get_specific_lottery_invaild_id(client):
    """test proper errpr is returned from the API
        target_url: /classrooms/<id>
    """
    idx = invalid_lottery_id  # lottery id to test
    resp = client.get('/lotteries/'+idx)

    assert resp.status_code == 404
    assert 'Lottery could not be found.' in resp.get_json()['message']


def test_apply(client):
    """attempt to apply new application.
        1. test: error isn't returned
        2. test: DB is changed
        target_url: /lotteries/<id> [POST]
    """
    idx = '1'
    token = login(client, test_user['username'],
                  test_user['g-recaptcha-response'])['token']
    resp = client.post('/lotteries/'+idx,
                       headers={'Authorization': 'Bearer ' + token})

    with client.application.app_context():
        # get needed objects
        target_lottery = Lottery.query.filter_by(id=idx).first()
        user = User.query.filter_by(username=test_user['username']).first()
        # this application should be added by previous 'client.put'
        application = Application.query.filter_by(
            lottery=target_lottery, user_id=user.id).first()

        assert application is not None
        assert resp.get_json() == application_schema.dump(application)[0]


@pytest.mark.skip(reason='not implemented yet')
def test_apply_noperm(client):
    """attempt to apply without proper permission.
        target_url: /lotteries/<id>/apply [POST]
    """
    idx = '1'
    token = login(client, admin['username'],
                  admin['g-recaptcha-response'])['token']
    resp = client.post('/lotteries/'+idx,
                       headers={'Authorization': 'Bearer ' + token})

    assert resp.status_code == 403
    assert 'no permission' in resp.get_json().keys()  # not completed yet


def test_apply_invaild(client):
    """attempt to apply to non-exsit lottery
        target_url: /lotteries/<id> [PUT]
    """
    idx = invalid_lottery_id
    token = login(client, test_user['username'],
                  test_user['g-recaptcha-response'])['token']
    resp = client.post('/lotteries/'+idx,
                       headers={'Authorization': 'Bearer ' + token})

    assert resp.status_code == 404
    assert 'Lottery could not be found.' in resp.get_json()['message']


def test_apply_already_done(client):
    """attempt to apply previously drawn application.
        1. test: error is returned
        target_url: /lotteries/<id> [POST]
    """
    idx = '1'
    token = login(client, test_user['username'],
                  test_user['g-recaptcha-response'])['token']

    with client.application.app_context():
        target_lottery = Lottery.query.filter_by(id=idx).first()
        target_lottery.done = True
        db.session.add(target_lottery)
        db.session.commit()

    resp = client.post('/lotteries/'+idx,
                       headers={'Authorization': 'Bearer ' + token})

    assert resp.status_code == 400
    assert 'already done' in resp.get_json()['message']


def test_apply_same_period(client):
    """attempt to apply to the same period with the previous application
        1. test: error is returned
        target_url: /lotteries/<id> [POST]
    """
    idx = '1'
    token = login(client, test_user['username'],
                  test_user['g-recaptcha-response'])['token']

    with client.application.app_context():
        target_lottery = Lottery.query.filter_by(id=idx).first()
        booking_lottery = Lottery.query.filter_by(
            index=target_lottery.index).filter(Lottery.id != idx).first()
        user = User.query.filter_by(username=test_user['username']).first()
        application = Application(lottery=booking_lottery, user_id=user.id)
        db.session.add(application)
        db.session.commit()

    resp = client.post('/lotteries/'+idx,
                       headers={'Authorization': 'Bearer ' + token})

    message = resp.get_json()['message']

    assert resp.status_code == 400
    assert 'already applying to a lottery in this period' in message


def test_get_allapplications(client):
    """test proper infomation is returned from the API
        target_url: /applications
    """
    lottery_id = 1
    make_application(client, test_user['username'], lottery_id)

    resp = as_user_get(
        client, test_user['username'], test_user['password'], f'/applications')

    with client.application.app_context():
        db_status = Application.query.all()
        application_list = applications_schema.dump(db_status)[0]

    assert resp.get_json() == application_list


def test_get_specific_application(client):
    """test proper infomation is returned from the API
        target_url: /applications/<id>
    """
    lottery_id = 1
    application_id = make_application(
        client, test_user['username'], lottery_id)

    resp = as_user_get(client,
                       test_user['username'], test_user['password'],
                       f'/applications/{application_id}')

    with client.application.app_context():
        db_status = Application.query.filter_by(id=application_id).first()
        application = application_schema.dump(db_status)[0]

    assert resp.get_json() == application


def test_get_specific_application_invaild_id(client):
    """test proper errpr is returned from the API
        target_url: /classrooms/<id>
    """
    lottery_id = 1
    application_id = make_application(
        client, test_user['username'], lottery_id)

    # application id to test
    idx = application_id + 1
    resp = as_user_get(client,
                       test_user['username'], test_user['password'],
                       f'/applications/{idx}')

    assert resp.status_code == 404
    assert 'Application could not be found.' in resp.get_json()['message']


def test_cancel(client):
    """test: cancel added application
        1. add new application to db
        2. send request to cancel
        3. check response's status_code and db status
        target_url: /applications/<id> [DELETE]
    """
    lottery_id = 1
    application_id = make_application(
        client, test_user['username'], lottery_id)

    token = login(client, test_user['username'],
                  test_user['g-recaptcha-response'])['token']
    user_resp = client.get('/status',
                           headers={'Authorization': 'Bearer ' + token})
    user_id = user_resp.get_json()['id']
    resp = client.delete(f'/applications/{application_id}',
                         headers={'Authorization': 'Bearer ' + token})
    with client.application.app_context():
        application = Application.query.filter_by(
            lottery_id=lottery_id, user_id=user_id).first()

    assert resp.status_code == 200
    assert application is None


def test_cancel_invaild(client):
    """attempt to cancel non-applied application.
        target_url: /applications/<id> [DELETE]
    """

    lottery_id = '1'
    token = login(client, test_user['username'],
                  test_user['g-recaptcha-response'])['token']
    resp = client.delete('/applications/' + lottery_id,
                         headers={'Authorization': 'Bearer ' + token})

    assert resp.status_code == 404
    assert "You're not applying for this lottery" in resp.get_json()['message']


def test_cancel_already_done(client):
    """attempt to cancel application that already-done lottery
        1. create 'done' application
        2. attempt to cancel that application
        target_url: /lotteries/<id> [DELETE]
    """
    token = login(client, test_user['username'],
                  test_user['g-recaptcha-response'])['token']
    lottery_id = 1
    application_id = make_application(
        client, test_user['username'], lottery_id)

    with client.application.app_context():
        target_application = Application.query.filter_by(
            id=application_id).first()
        target_application.status = 'lose'
        db.session.add(target_application)
        db.session.commit()

    resp = client.delete(f'/applications/{application_id}',
                         headers={'Authorization': 'Bearer ' + token})

    assert resp.status_code == 400
    assert 'The Application has already fullfilled' in resp.get_json()[
        'message']


@pytest.mark.skip(reason='not implemented yet')
def test_cancel_noperm(client):
    """attempt to cancel without permission
        1. create new application.
        2. attempt to cancel with other user's token
    """
    idx = '1'
    owner = test_user
    user = {'username': 'hoge', 'g-recaptcha-response': 'hugo'}
    owner_token = login(client, owner['username'],
                          owner['g-recaptcha-response'])['token']
    user_token = login(client, user['username'],
                          user['g-recaptcha-response'])['token']

    client.post('/lotteries/' + idx,
                headers={'Authorization': 'Bearer' + owner_token})
    resp = client.delete('/applications/' + idx,
                         headers={'Authorization': 'Bearer ' + user_token})

    assert resp.status_code == 403
    assert 'insufficient_scope' in resp.headers['WWW-Authenticate']


def test_draw(client):
    """attempt to draw a lottery
        1. make some applications to one lottery
        2. draws the lottery
        3. test: status code, whether winner status is returned
        4. test: DB is changed
        target_url: /lotteries/<id>/apply [PUT]
    """
    idx = '1'

    with client.application.app_context():
        target_lottery = Lottery.query.filter_by(id=idx).first()
        users = User.query.all()
        for user in users:
            application = Application(lottery=target_lottery, user_id=user.id)
            db.session.add(application)
        db.session.commit()

    token = login(client, admin['username'],
                  admin['g-recaptcha-response'])['token']
    resp = client.post('/lotteries/'+idx+'/draw',
                       headers={'Authorization': 'Bearer ' + token})

    assert resp.status_code == 200

    chosen_id = resp.get_json()[0]['id']
    with client.application.app_context():
        user = User.query.filter_by(id=chosen_id).first()

        assert user is not None
        assert resp.get_json()[0] == user_schema.dump(user)[0]

        target_lottery = Lottery.query.filter_by(id=idx).first()
        assert target_lottery.done
        users = User.query.all()
        for user in users:
            application = Application.query.filter_by(
                lottery=target_lottery, user_id=user.id).first()
            status = 'won' if user.id == chosen_id else 'lose'
            assert application.status == status


def test_draw_noperm(client):
    """attempt to draw without proper permission.
        target_url: /lotteries/<id>/draw [POST]
    """
    idx = '1'
    token = login(client, test_user['username'],
                  test_user['g-recaptcha-response'])['token']
    resp = client.post('/lotteries/'+idx+'/draw',
                       headers={'Authorization': 'Bearer ' + token})

    assert resp.status_code == 403
    assert 'Forbidden' in resp.get_json()['message']


def test_draw_invaild(client):
    """attempt to draw non-exsit lottery
        target_url: /lotteries/<id>/draw [POST]
    """
    idx = invalid_lottery_id
    token = login(client, admin['username'],
                  admin['g-recaptcha-response'])['token']
    resp = client.post('/lotteries/'+idx+'/draw',
                       headers={'Authorization': 'Bearer ' + token})

    assert resp.status_code == 404
    assert 'Lottery could not be found.' in resp.get_json()['message']


def test_draw_already_done(client):
    """attempt to draw previously drawn lottery.
        1. test: error is returned
        target_url: /lotteries/<id>/draw [POST]
    """
    idx = '1'
    token = login(client, admin['username'],
                  admin['g-recaptcha-response'])['token']

    with client.application.app_context():
        target_lottery = Lottery.query.filter_by(id=idx).first()
        target_lottery.done = True
        db.session.add(target_lottery)
        db.session.commit()

    resp = client.post('/lotteries/'+idx+'/draw',
                       headers={'Authorization': 'Bearer ' + token})

    assert resp.status_code == 400
    assert 'already done' in resp.get_json()['message']


@pytest.mark.skip(reason='not implemented yet')
def test_draw_nobody_apply(client):
    """attempt to draw a lottery that nobody applying
        1. make sure any application is applied to the lottery
        2. attempt to draw it
        target_url: /lotteries/<id>/draw [POST]
    """

    idx = '1'
    token = login(client, admin['username'], admin['password'])['token']

    with client.application.app_context():
        target_applications = Application.query.filter_by(lottery_id=idx).all()
        if target_applications is not None:
            db.session.delete(target_applications)
            db.session.commit()

    resp = client.post('/lotteries/'+idx+'/draw',
                       headers={'Authorization': 'Bearer ' + token})

    assert resp.status_code == 400
    assert 'nobody' in resp.get_json()['message']
