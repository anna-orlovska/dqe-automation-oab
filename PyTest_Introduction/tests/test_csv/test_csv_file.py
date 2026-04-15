import pytest
import re


@pytest.mark.validate_csv
def test_file_not_empty(csv_data):
    assert not csv_data.empty


@pytest.mark.xfail
def test_duplicates(csv_data):
    duplicate_rows = csv_data[csv_data.duplicated()]
    count = len(duplicate_rows)
    assert duplicate_rows.empty, f"Found {count} duplicate rows"


@pytest.mark.validate_csv
def test_validate_schema(validate_schema):
    # Next assert checks if final dataframe is returned (not empty).
    # It is returned only in case the fixture 'validate_schema' doesn't return any errors
    assert not validate_schema.empty


@pytest.mark.validate_csv
@pytest.mark.skip
def test_age_column_valid(validate_schema):
    df = validate_schema
    is_age_valid = df['age'].between(0, 100, inclusive='both')
    invalid_ages = df[~is_age_valid]
    assert invalid_ages.empty, f"Found {invalid_ages.count()} invalid ages"


@pytest.mark.validate_csv
def test_email_column_valid(validate_schema):
    df = validate_schema

    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    is_email_valid = df['email'].str.contains(email_regex, regex=True, na=False)
    invalid_emails = df[~is_email_valid]
    assert invalid_emails.empty, (
        f"Found {invalid_emails.count()} invalid emails: \n"
        f"{invalid_emails[['id', 'name', 'email']]}"
    )


@pytest.mark.parametrize("user_id, expected_status", [
    (1, False),
    (2, True)
])
def test_active_players(validate_schema, user_id, expected_status):
    df = validate_schema
    user_rows = df[df['id'] == user_id]
    assert not user_rows.empty, f"User with id {user_id} not found"
    actual_status = user_rows['is_active'].values[0]
    assert actual_status == expected_status, (
        f"Error for user with id {user_id}. Expected {expected_status}, actual {actual_status}"
    )


def test_active_player(validate_schema):
    df = validate_schema
    user_row = df[df['id'] == 2]
    assert not user_row.empty, "User with id 2 not found"
