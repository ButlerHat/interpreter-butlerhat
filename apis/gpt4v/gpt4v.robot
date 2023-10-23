*** Settings ***
Library   ButlerRobot.AIBrowserLibrary  stealth_mode=${True}  record=${False}  fix_bbox=${False}  presentation_mode=${False}   console=${False}  WITH NAME  Browser
Library   OperatingSystem


*** Variables ***
${COOKIES_DIR}  /tmp/cookies/cookies
${STATE_JSON}  /tmp/cookies/cookies.json
${IMAGE_PATH}     /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/interpreter-butlerhat/apis/gpt4v/images/descarga.png
${PROMPT}    Is the red bounding box centered in the search bar?


*** Test Cases ***
Test GTP4-V
    Create Chat with cookies  ${STATE_JSON}

Test GTP4-V Generate
    ${response}  Generate GPT4-V
    Log  ${response}  console=${True}

Test GTP4-V Remove
    ${response}  Generate GPT4-V
    Log  ${response}  console=${True}
    Run Keyword And Ignore Error  Remove current chat
    

*** Keywords ***
Create Chat with cookies
    [Arguments]  ${STATE_JSON}
    Close Browser  ALL
    Browser.New Stealth Persistent Context   userDataDir=${COOKIES_DIR}   browser=chromium  url=https://chat.openai.com/
    
    Wait Until Network Is Idle  timeout=30s
    ${is_logged}  Is loged in?
    IF  not ${is_logged}
        Should Exist    path=${STATE_JSON}  msg=State file not found.
        Browser.Add All Cookies From State  ${STATE_JSON}
        Close Browser  ALL
        Browser.New Stealth Persistent Context   userDataDir=${COOKIES_DIR}   browser=chromium  url=https://chat.openai.com/
    END

    Wait Until Network Is Idle  timeout=10s
    Run Keyword And Ignore Error  Accept popup
    Create new chat

    Click on GPT4
    Click on Default

Reload ChatGPT
    Run Keyword And Ignore Error   Remove current chat
    Reload


Remove current chat
    Click on trash icon
    Click on Delete

Open Browser if not exists
    [Arguments]  ${STATE_JSON}
    ${is_browser}  Is browser?
    IF  not ${is_browser}  Create Chat with cookies  ${STATE_JSON}

Generate GPT4-V
    Open Browser if not exists  ${STATE_JSON}

    Upload image   ${IMAGE_PATH}
    ${response}  Send Message   ${PROMPT}
    RETURN  ${response}


Is browser?
    ${browser_list}  Get Browser Ids
    TRY
        Length Should Be    ${browser_list}    1
    EXCEPT
        RETURN  ${False}
    END
    RETURN  ${True}

Is loged in?
    TRY
        Wait For Elements State    //button[contains(.,'GPT-4')]  visible  timeout=5s
    EXCEPT
        RETURN  ${False}
    END
    RETURN  ${True}

Click on trash icon
    Click  //ol//a//button[2]

Click on Delete
    Click  //button[contains(.,"Delete")]
    
Accept popup
    ${old_timeout}  Set Browser Timeout    3
    TRY
        Click  //div[contains(text(),'Okay')]
    FINALLY
        Set Browser Timeout    ${old_timeout}
    END
    
Click on GPT4
    Click  //button[contains(.,'GPT-4')]

Click on Default
    ${old_timeout}  Set Browser Timeout    10
    Mouse Move Relative To  //button[contains(.,'GPT-4')]
    Click  //*[contains(text(),'Default')]
    Set Browser Timeout    ${old_timeout}

Create new chat
    Click  //a[contains(.,'New Chat')]

Upload Image
    [Tags]  no_record
    [Arguments]  ${path}
    Upload File By Selector    //input[@type='file']    ${path}

Send message
    [Arguments]  ${message}
    Wait For Elements State    //button[contains(.,"Stop")]  hidden   timeout=1m
    ${num_messages}  Get Element Count  //main//div[contains(@data-testid,"conversation-turn-")]
    Type Text    //*[@id="prompt-textarea"]    ${message}
    Wait For Elements State    //*[@data-testid="send-button"]  enabled
    Click  //*[@data-testid="send-button"]
    
    Wait For Elements State    //button[contains(.,"Stop")]  visible   timeout=1m
    Wait For Elements State    //button[contains(.,"Stop")]  hidden   timeout=1m
    
    # Start in 2 + 1 for the message send
    ${response_id}  Evaluate  ${num_messages}+3
    ${response}  Get Text  //main//div[contains(@data-testid,"conversation-turn-${response_id}")]
    
    RETURN  ${response}
