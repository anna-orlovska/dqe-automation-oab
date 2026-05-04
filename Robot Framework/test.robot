*** Settings ***
Library         helper.py
Library         Collections
Documentation    Comparison of HTML report data with Parquet dataset


*** Variables ***
${REPORT_FILE}        ${EXECDIR}/report.html
${PARQUET_FOLDER}   ${CURDIR}/../../parquet_data
${FILTER_DATE}        2026-03-23


*** Keywords ***
Extract HTML Report Data
    ${rows}=    Extract Table From Report    ${REPORT_FILE}
    RETURN      ${rows}

Get HTML Rows For Date
    [Arguments]    ${rows}    ${date}
    ${filtered}=    Filter By Date    ${rows}    ${date}
    RETURN          ${filtered}

Get Parquet Rows For Date
    ${rows}=    Read Parquet Data    ${PARQUET_FOLDER}    ${FILTER_DATE}
    RETURN      ${rows}

Compare Data
    [Arguments]    ${html_rows}    ${parquet_rows}
    ${result}=    Compare Report And Parquet    ${html_rows}    ${parquet_rows}
    RETURN        ${result}

*** Test Cases ***
Verify HTML Report Matches Parquet Data
    [Documentation]    Extracts data from HTML report and Parquet,
    ...                filters by date and compares results

    # Step 1 - get data from HTML
    ${all_html_rows}=     Extract HTML Report Data
    ${html_rows}=         Get HTML Rows For Date    ${all_html_rows}    ${FILTER_DATE}

    # Step 2 - reading Parquet
    ${parquet_rows}=      Get Parquet Rows For Date

    Log    HTML rows count: ${html_rows.__len__()}
    Log    Parquet rows count: ${parquet_rows.__len__()}
    Log    HTML data: ${html_rows}
    Log    Parquet data: ${parquet_rows}

    # Step 3 - comparison
    ${result}=            Compare Data    ${html_rows}    ${parquet_rows}

    # Step 4 - check results
    Should Be True        ${result}[match]
    ...                   Data mismatch found: ${result}[mismatches]





