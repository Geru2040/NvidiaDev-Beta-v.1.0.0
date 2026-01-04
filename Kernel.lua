-- Lumen Command Executor for Delta Executor
-- Listens for commands from terminal and executes them

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local TeleportService = game:GetService("TeleportService")

-- API Configuration
local API_BASE = "https://lseypdqwyekqdndladsk.supabase.co/functions/v1"
local COMMANDS_ENDPOINT = API_BASE .. "/commands"
local RESPONSE_ENDPOINT = API_BASE .. "/command-response"
local API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxzZXlwZHF3eWVrcWRuZGxhZHNrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY4NzYyNzQsImV4cCI6MjA4MjQ1MjI3NH0.-Ebx3SwdHhEAkUg_TYPIxPktVI5Q-vRU1wxo69p7n90"

-- Auto-detect account ID
local LocalPlayer = Players.LocalPlayer
local ACCOUNT_ID = tostring(LocalPlayer.UserId)

-- DEX state tracker
local dexLoaded = false

-- Global flowwatch state
local FlowWatchActive = false
local FlowWatchState = {}

-- Agent mode detection
local IS_AGENT_MODE = false
local AGENT_START_TIME = tick()
local AGENT_GAME_JOIN_TIME = tick()

-- Check if request function exists
local request = (syn and syn.request) or (http and http.request) or http_request or (fluxus and fluxus.request) or request

if not request then
    warn("✗ HTTP request function not found!")
    return
end

-- Anti-AFK system for agent mode
local function startAntiAFK()
    spawn(function()
        local VirtualUser = game:GetService("VirtualUser")
        LocalPlayer.Idled:Connect(function()
            VirtualUser:CaptureController()
            VirtualUser:ClickButton2(Vector2.new())
        end)

        while IS_AGENT_MODE do
            wait(60)
            pcall(function()
                if LocalPlayer.Character and LocalPlayer.Character:FindFirstChild("HumanoidRootPart") then
                    local hrp = LocalPlayer.Character.HumanoidRootPart
                    hrp.CFrame = hrp.CFrame * CFrame.new(0, 0.1, 0)
                end
            end)
        end
    end)
end

-- Global screenshot URL storage
_G.LUMEN_SCREENSHOT_URL = nil
_G.LUMEN_VIDEO_URL = nil

local function captureScreenshot()
    local RESOLUTION = { width = 854, height = 480 }
    local UPLOAD_URL = "https://mcsvrkxjnomlvzmqfuxq.supabase.co/functions/v1/upload"
    local AGENT_ID = HttpService:GenerateGUID(false)
    local camera = workspace.CurrentCamera
    local Lighting = game:GetService("Lighting")

    local function base64encode(data)
        if crypt and crypt.base64 and crypt.base64.encode then return crypt.base64.encode(data) end
        local b='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
        return ((data:gsub('.', function(x)
            local r,bits='',x:byte()
            for i=8,1,-1 do r=r..(bits%2^i-bits%2^(i-1)>0 and '1' or '0') end
            return r
        end)..'0000'):gsub('%d%d%d?%d?%d?%d?', function(x)
            if #x<6 then return '' end
            local c=0
            for i=1,6 do c=c+(x:sub(i,i)=='1' and 2^(6-i) or 0) end
            return b:sub(c+1,c+1)
        end)..({ '', '==', '=' })[#data%3+1])
    end

    local function getISO8601Timestamp()
        local t=os.date("!*t")
        return string.format("%04d-%02d-%02dT%02d:%02d:%02dZ", t.year,t.month,t.day,t.hour,t.min,t.sec)
    end

    local SNAPSHOT_CFRAME = camera.CFrame
    local SNAPSHOT_FOV = camera.FieldOfView
    local VIEWPORT_SIZE = camera.ViewportSize

    local IS_DAYTIME = Lighting.ClockTime >= 6 and Lighting.ClockTime < 18
    local ENABLE_SHADOWS = Lighting.GlobalShadows and IS_DAYTIME
    local LIGHT_DIRECTION = IS_DAYTIME and Lighting:GetSunDirection() or Lighting:GetMoonDirection()

    local rayParams = RaycastParams.new()
    rayParams.FilterType = Enum.RaycastFilterType.Blacklist

    local shadowRayParams = RaycastParams.new()
    shadowRayParams.FilterType = Enum.RaycastFilterType.Blacklist
    if LocalPlayer.Character then shadowRayParams.FilterDescendantsInstances = {LocalPlayer.Character} end

    local function getPixel(x, y)
        local screenX = ((x+0.5)/RESOLUTION.width)*2-1
        local screenY = -(((y+0.5)/RESOLUTION.height)*2-1)
        local aspectRatio = VIEWPORT_SIZE.X / VIEWPORT_SIZE.Y
        local heightScale = math.tan(math.rad(SNAPSHOT_FOV)/2)
        local widthScale = heightScale * aspectRatio
        local worldDir = SNAPSHOT_CFRAME:VectorToWorldSpace(Vector3.new(screenX * widthScale, screenY * heightScale, -1).Unit)

        local hit = workspace:Raycast(SNAPSHOT_CFRAME.Position, worldDir*1000, rayParams)
        if hit and hit.Instance then
            local color = hit.Instance.Color or Color3.new(0.5, 0.5, 0.5)
            local r, g, b = color.R*255, color.G*255, color.B*255
            if ENABLE_SHADOWS and hit.Normal:Dot(-LIGHT_DIRECTION) > 0.1 then
                local shadowRay = workspace:Raycast(hit.Position + hit.Normal*0.05, -LIGHT_DIRECTION*500, shadowRayParams)
                if shadowRay then r, g, b = r*0.5, g*0.5, b*0.5 end
            end
            return math.floor(r), math.floor(g), math.floor(b)
        end
        return 135, 206, 235
    end

    spawn(function()
        local pixels = {}
        local lastYield = tick()
        for y = 0, RESOLUTION.height - 1 do
            for x = 0, RESOLUTION.width - 1 do
                local r, g, b = getPixel(x, y)
                local idx = (y * RESOLUTION.width + x) * 4 + 1
                pixels[idx], pixels[idx+1], pixels[idx+2], pixels[idx+3] = r, g, b, 255
            end
            if tick() - lastYield > 0.05 then task.wait(); lastYield = tick() end
        end

        local function writeInt(v, bytes)
            local s=""
            for i=1,bytes do s=s..string.char(v%256); v=math.floor(v/256) end
            return s
        end

        local row = math.ceil(RESOLUTION.width * 3 / 4) * 4
        local bmp = "BM" .. writeInt(54 + row*RESOLUTION.height, 4) .. writeInt(0, 4) .. writeInt(54, 4)
        bmp = bmp .. writeInt(40, 4) .. writeInt(RESOLUTION.width, 4) .. writeInt(RESOLUTION.height, 4) .. writeInt(1, 2) .. writeInt(24, 2) .. writeInt(0, 4)
        bmp = bmp .. writeInt(row*RESOLUTION.height, 4) .. writeInt(2835, 4) .. writeInt(2835, 4) .. writeInt(0, 4) .. writeInt(0, 4)
        for y = RESOLUTION.height - 1, 0, -1 do
            local row_data = {}
            for x = 0, RESOLUTION.width - 1 do
                local i = (y * RESOLUTION.width + x) * 4 + 1
                table.insert(row_data, string.char(pixels[i + 2], pixels[i + 1], pixels[i]))
            end
            bmp = bmp .. table.concat(row_data) .. string.rep("\0", row - RESOLUTION.width * 3)
        end

        local success, response = pcall(function()
            return request({
                Url = UPLOAD_URL,
                Method = "POST",
                Headers = {["Content-Type"] = "application/json"},
                Body = HttpService:JSONEncode({
                    agent_id = AGENT_ID,
                    place_id = game.PlaceId,
                    timestamp = getISO8601Timestamp(),
                    image_data = base64encode(bmp),
                    resolution = RESOLUTION.width .. "x" .. RESOLUTION.height
                })
            })
        end)

        if success and (response.Success or response.StatusCode == 200) then
            local decoded = HttpService:JSONDecode(response.Body)
            _G.LUMEN_SCREENSHOT_URL = decoded.url
        else
            _G.LUMEN_SCREENSHOT_URL = "ERROR: " .. tostring(response and response.StatusCode or "Unknown")
        end
    end)
    return true
end

-- Agent command handlers
local AgentCommands = {}

local function captureScreenrecord(duration)
    local FPS = 10
    local DURATION = math.min(duration or 5, 5)
    local RESOLUTION = { width = 160, height = 90 }
    local TOTAL_FRAMES = FPS * DURATION
    local API_URL = "https://dhcrqadofygjujukyszj.supabase.co/functions/v1/upload-frames"
    local AGENT_ID = HttpService:GenerateGUID(false)
    local camera = workspace.CurrentCamera
    local RunService = game:GetService("RunService")

    local function b64(data)
        local b='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
        return ((data:gsub('.', function(x)
            local r,bits='',x:byte()
            for i=8,1,-1 do r=r..(bits%2^i-bits%2^(i-1)>0 and '1' or '0') end
            return r
        end)..'0000'):gsub('%d%d%d?%d?%d?%d?', function(x)
            if #x<6 then return '' end
            local c=0
            for i=1,6 do c=c+(x:sub(i,i)=='1' and 2^(6-i) or 0) end
            return b:sub(c+1,c+1)
        end)..({ '', '==', '=' })[#data%3+1])
    end

    local function captureFrameInstant()
        local pixels = table.create(RESOLUTION.width * RESOLUTION.height * 3)
        local idx = 1
        local rayParams = RaycastParams.new()
        rayParams.FilterType = Enum.RaycastFilterType.Exclude
        if LocalPlayer.Character then rayParams.FilterDescendantsInstances = { LocalPlayer.Character } end
        
        local vpWidth = camera.ViewportSize.X
        local vpHeight = camera.ViewportSize.Y
        local scaleX = vpWidth / RESOLUTION.width
        local scaleY = vpHeight / RESOLUTION.height

        for y = 0, RESOLUTION.height - 1 do
            for x = 0, RESOLUTION.width - 1 do
                local vp = Vector2.new((x + 0.5) * scaleX, (y + 0.5) * scaleY)
                local ray = camera:ViewportPointToRay(vp.X, vp.Y)
                local hit = workspace:Raycast(ray.Origin, ray.Direction * 500, rayParams)
                
                local r, g, b = 135, 206, 235
                if hit and hit.Instance then
                    local c = hit.Instance.Color
                    r, g, b = math.floor(c.R * 255), math.floor(c.G * 255), math.floor(c.B * 255)
                end
                pixels[idx], pixels[idx + 1], pixels[idx + 2] = r, g, b
                idx = idx + 3
            end
        end
        return pixels
    end

    local function bmp(pixels, width, height)
        local function w16(v) return string.char(v % 256, math.floor(v / 256) % 256) end
        local function w32(v)
            return string.char(v % 256, math.floor(v / 256) % 256, 
                               math.floor(v / 65536) % 256, math.floor(v / 16777216) % 256)
        end
        local rowPad = (4 - (width * 3) % 4) % 4
        local rowSize = width * 3 + rowPad
        local pixelDataSize = rowSize * height
        local header = "BM" .. w32(54 + pixelDataSize) .. w32(0) .. w32(54) ..
            w32(40) .. w32(width) .. w32(height) .. w16(1) .. w16(24) ..
            w32(0) .. w32(pixelDataSize) .. w32(2835) .. w32(2835) .. w32(0) .. w32(0)
        local rows = {}
        local padding = string.rep("\0", rowPad)
        for y = height - 1, 0, -1 do
            local row = {}
            for x = 0, width - 1 do
                local i = (y * width + x) * 3 + 1
                row[#row + 1] = string.char(pixels[i + 2], pixels[i + 1], pixels[i])
            end
            rows[#rows + 1] = table.concat(row) .. padding
        end
        return header .. table.concat(rows)
    end

    spawn(function()
        local frames = {}
        local recordStart = os.clock()
        local frameCount = 0
        local targetInterval = 1 / FPS
        local lastFrameTime = 0
        
        while frameCount < TOTAL_FRAMES do
            local elapsed = os.clock() - recordStart
            if elapsed - lastFrameTime >= targetInterval then
                local px = captureFrameInstant()
                local img = bmp(px, RESOLUTION.width, RESOLUTION.height)
                frameCount = frameCount + 1
                frames[frameCount] = {
                    index = frameCount - 1,
                    timestamp = math.floor(elapsed * 1000),
                    image_base64 = b64(img)
                }
                lastFrameTime = elapsed
            end
            task.wait()
        end

        local payload = {
            agent_id = AGENT_ID,
            place_id = game.PlaceId,
            fps = FPS,
            duration = DURATION,
            resolution = RESOLUTION.width .. "x" .. RESOLUTION.height,
            frames = frames
        }

        local success, result = pcall(function()
            return request({
                Url = API_URL,
                Method = "POST",
                Headers = { ["Content-Type"] = "application/json" },
                Body = HttpService:JSONEncode(payload)
            })
        end)

        if success and (result.Success or result.StatusCode == 200) then
            local data = HttpService:JSONDecode(result.Body)
            _G.LUMEN_VIDEO_URL = data.video_url
        else
            _G.LUMEN_VIDEO_URL = "ERROR"
        end
    end)
    return true
end

AgentCommands.agent_screenrecord = function(args)
    _G.LUMEN_VIDEO_URL = "PENDING"
    captureScreenrecord(args and args.duration)
    return { success = true, message = "Screen recording started" }
end

AgentCommands.agent_screenrecord_status = function(args)
    return { success = true, data = _G.LUMEN_VIDEO_URL or "PENDING" }
end

AgentCommands.exe = function(args)
    return AgentCommands.agent_execute(args)
end

AgentCommands.screenshot = function(args)
    _G.LUMEN_SCREENSHOT_URL = "PENDING"
    captureScreenshot()
    return { success = true, message = "Screenshot capture started" }
end

AgentCommands.screenshot_status = function(args)
    return { success = true, data = _G.LUMEN_SCREENSHOT_URL or "PENDING" }
end

AgentCommands.agent_ping = function(args)
    return {
        success = true,
        message = "pong",
        agent_id = ACCOUNT_ID,
        is_agent = IS_AGENT_MODE
    }
end

AgentCommands.agent_status = function(args)
    local currentGame = nil

    pcall(function()
        currentGame = {
            name = game:GetService("MarketplaceService"):GetProductInfo(game.PlaceId).Name,
            place_id = game.PlaceId,
            players = #Players:GetPlayers(),
            time_in_game = math.floor((tick() - AGENT_GAME_JOIN_TIME) / 60)
        }
    end)

    return {
        success = true,
        status = "online",
        uptime = math.floor((tick() - AGENT_START_TIME) / 60),
        current_game = currentGame,
        anti_afk_active = IS_AGENT_MODE,
        agent_id = ACCOUNT_ID
    }
end

AgentCommands.agent_attach = function(args)
    local placeId = args and args.place_id
    local autoScript = args and args.auto_script

    if not placeId then
        return {
            success = false,
            error = "No place_id provided"
        }
    end

    if type(placeId) == "string" then
        placeId = tonumber(placeId)
    end

    if not placeId then
        return {
            success = false,
            error = "Invalid place_id format"
        }
    end

    IS_AGENT_MODE = true
    startAntiAFK()

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🎯 Smart Teleport to Place ID:", placeId)
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    local teleportSuccess = false
    local teleportMethod = "Unknown"

    -- Method 1: Standard TeleportService (same universe)
    print("\n[1/5] Trying standard teleport...")
    local success1 = pcall(function()
        TeleportService:Teleport(placeId, LocalPlayer)
        teleportSuccess = true
        teleportMethod = "TeleportService"
        print("✓ Standard teleport initiated!")
    end)

    if teleportSuccess then
        if autoScript then
            spawn(function()
                wait(8)
                pcall(function()
                    if autoScript:match("^https?://") then
                        loadstring(game:HttpGet(autoScript, true))()
                    else
                        loadstring(autoScript)()
                    end
                end)
            end)
        end

        return {
            success = true,
            message = "Teleporting to game",
            method = "TeleportService",
            place_id = placeId
        }
    end
    print("✗ Standard teleport failed")

    -- Method 2: Deep Link (Mobile & Cross-Universe)
    print("\n[2/5] Trying deep link...")
    local success2 = pcall(function()
        local deepLinkUrl = string.format("roblox://placeId=%d", placeId)

        local deepLinkWorked = false

        -- Try syn.request
        if not deepLinkWorked and syn and syn.request then
            pcall(function()
                syn.request({
                    Url = deepLinkUrl,
                    Method = "GET"
                })
                deepLinkWorked = true
                print("✓ Deep link via syn.request")
            end)
        end

        -- Try request
        if not deepLinkWorked and request then
            pcall(function()
                request({
                    Url = deepLinkUrl,
                    Method = "GET"
                })
                deepLinkWorked = true
                print("✓ Deep link via request")
            end)
        end

        -- Try http_request
        if not deepLinkWorked and http_request then
            pcall(function()
                http_request({
                    Url = deepLinkUrl,
                    Method = "GET"
                })
                deepLinkWorked = true
                print("✓ Deep link via http_request")
            end)
        end

        -- Try http.request
        if not deepLinkWorked and http and http.request then
            pcall(function()
                http.request({
                    Url = deepLinkUrl,
                    Method = "GET"
                })
                deepLinkWorked = true
                print("✓ Deep link via http.request")
            end)
        end

        if deepLinkWorked then
            teleportSuccess = true
            teleportMethod = "DeepLink"
        end
    end)

    if teleportSuccess then
        if autoScript then
            spawn(function()
                wait(8)
                pcall(function()
                    if autoScript:match("^https?://") then
                        loadstring(game:HttpGet(autoScript, true))()
                    else
                        loadstring(autoScript)()
                    end
                end)
            end)
        end

        return {
            success = true,
            message = "Deep link teleport initiated",
            method = "DeepLink",
            place_id = placeId
        }
    end
    print("✗ Deep link failed")

    -- Method 3: Browser Launch
    print("\n[3/5] Trying browser launch...")
    local success3 = pcall(function()
        local url = string.format("https://www.roblox.com/games/start?placeId=%d", placeId)

        pcall(function()
            game:GetService("GuiService"):OpenBrowserWindow(url)
            teleportSuccess = true
            teleportMethod = "Browser"
            print("✓ Browser opened")
        end)
    end)

    if teleportSuccess then
        return {
            success = true,
            message = "Browser teleport initiated",
            method = "Browser",
            place_id = placeId,
            note = "Game opened in browser - click Join Game"
        }
    end
    print("✗ Browser failed")

    -- Method 4: GuiService
    print("\n[4/5] Trying GuiService...")
    local success4 = pcall(function()
        game:GetService("GuiService"):OpenBrowserWindow(
            string.format("https://www.roblox.com/games/start?placeId=%d", placeId)
        )
        teleportSuccess = true
        teleportMethod = "GuiService"
        print("✓ GuiService opened")
    end)

    if teleportSuccess then
        return {
            success = true,
            message = "GuiService teleport initiated",
            method = "GuiService",
            place_id = placeId
        }
    end
    print("✗ GuiService failed")

    -- Method 5: Clipboard (Always works)
    print("\n[5/5] Using clipboard method...")
    local gameUrl = string.format("https://www.roblox.com/games/%d", placeId)

    if setclipboard then
        setclipboard(gameUrl)
        print("✓ Game URL copied to clipboard")
    end

    -- Show GUI with instructions
    pcall(function()
        local ScreenGui = Instance.new("ScreenGui")
        ScreenGui.Name = "LumenTeleport"
        ScreenGui.ResetOnSpawn = false
        ScreenGui.Parent = game:GetService("CoreGui")

        local Frame = Instance.new("Frame")
        Frame.Size = UDim2.new(0, 350, 0, 200)
        Frame.Position = UDim2.new(0.5, -175, 0.5, -100)
        Frame.BackgroundColor3 = Color3.fromRGB(40, 40, 40)
        Frame.BorderSizePixel = 0
        Frame.Parent = ScreenGui

        local UICorner = Instance.new("UICorner")
        UICorner.CornerRadius = UDim.new(0, 12)
        UICorner.Parent = Frame

        local Title = Instance.new("TextLabel")
        Title.Size = UDim2.new(1, -20, 0, 40)
        Title.Position = UDim2.new(0, 10, 0, 10)
        Title.BackgroundTransparency = 1
        Title.Text = "🎮 Lumen Teleport"
        Title.TextColor3 = Color3.fromRGB(200, 150, 255)
        Title.TextSize = 18
        Title.Font = Enum.Font.GothamBold
        Title.Parent = Frame

        local Info = Instance.new("TextLabel")
        Info.Size = UDim2.new(1, -20, 0, 100)
        Info.Position = UDim2.new(0, 10, 0, 50)
        Info.BackgroundTransparency = 1
        Info.Text = string.format("Place ID: %d\n\nURL copied to clipboard!\nPaste in Roblox to join", placeId)
        Info.TextColor3 = Color3.fromRGB(255, 255, 255)
        Info.TextSize = 14
        Info.Font = Enum.Font.Gotham
        Info.TextWrapped = true
        Info.TextYAlignment = Enum.TextYAlignment.Top
        Info.Parent = Frame

        local CloseButton = Instance.new("TextButton")
        CloseButton.Size = UDim2.new(0, 100, 0, 35)
        CloseButton.Position = UDim2.new(0.5, -50, 1, -45)
        CloseButton.BackgroundColor3 = Color3.fromRGB(150, 100, 255)
        CloseButton.Text = "Close"
        CloseButton.TextColor3 = Color3.fromRGB(255, 255, 255)
        CloseButton.TextSize = 14
        CloseButton.Font = Enum.Font.GothamBold
        CloseButton.Parent = Frame

        local ButtonCorner = Instance.new("UICorner")
        ButtonCorner.CornerRadius = UDim.new(0, 8)
        ButtonCorner.Parent = CloseButton

        CloseButton.MouseButton1Click:Connect(function()
            ScreenGui:Destroy()
        end)

        task.delay(15, function()
            if ScreenGui and ScreenGui.Parent then
                ScreenGui:Destroy()
            end
        end)
    end)

    print("✓ Clipboard method ready")
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    return {
        success = true,
        message = "Clipboard method ready",
        method = "Clipboard (Manual)",
        place_id = placeId,
        note = "Game URL copied - paste in Roblox to join"
    }
end

AgentCommands.agent_leave_game = function(args)
    game:Shutdown()
    return {
        success = true,
        message = "Leaving game"
    }
end

AgentCommands.agent_execute = function(args)
    local script = args and args.script

    if not script then
        return {
            success = false,
            error = "No script provided"
        }
    end

    local success, err = pcall(function()
        if script:match("^https?://") then
            loadstring(game:HttpGet(script, true))()
        else
            loadstring(script)()
        end
    end)

    if success then
        return {
            success = true,
            message = "Script executed on agent"
        }
    else
        return {
            success = false,
            error = tostring(err)
        }
    end
end

AgentCommands.agent_collect_data = function(args)
    local data = {
        game_info = {
            name = game:GetService("MarketplaceService"):GetProductInfo(game.PlaceId).Name,
            place_id = game.PlaceId,
            creator = game.CreatorId
        },
        players = {},
        scripts_count = 0
    }

    for _, player in pairs(Players:GetPlayers()) do
        table.insert(data.players, {
            name = player.Name,
            id = player.UserId,
            team = player.Team and player.Team.Name or "None"
        })
    end

    for _, descendant in pairs(game:GetDescendants()) do
        if descendant:IsA("Script") or descendant:IsA("LocalScript") or descendant:IsA("ModuleScript") then
            data.scripts_count = data.scripts_count + 1
        end
    end

    return {
        success = true,
        data = data
    }
end

AgentCommands.agent_disconnect = function(args)
    IS_AGENT_MODE = false
    return {
        success = true,
        message = "Agent mode disabled"
    }
end

-- Regular command handlers
local CommandHandlers = {}

CommandHandlers.screenrecord = function(args)
    _G.LUMEN_VIDEO_URL = "PENDING"
    captureScreenrecord(args and args.duration)
    return { success = true, message = "Screen recording started" }
end

CommandHandlers.screenrecord_status = function(args)
    return { success = true, data = _G.LUMEN_VIDEO_URL or "PENDING" }
end

CommandHandlers.screenshot = function(args)
    _G.LUMEN_SCREENSHOT_URL = "PENDING"
    captureScreenshot()
    return { success = true, message = "Screenshot capture started" }
end

CommandHandlers.screenshot_status = function(args)
    return { success = true, data = _G.LUMEN_SCREENSHOT_URL or "PENDING" }
end

CommandHandlers.ping = function(args)
    return {
        success = true,
        message = "pong",
        timestamp = os.time()
    }
end

CommandHandlers.hotspot = function(args)
    print("🔥 Scanning for script hotspots...")

    local scripts = {}
    local count = 0
    local maxScripts = 100

    for _, descendant in pairs(game:GetDescendants()) do
        if count >= maxScripts then break end

        if descendant:IsA("LocalScript") or descendant:IsA("Script") or descendant:IsA("ModuleScript") then
            local sourceLength = 0
            local lineCount = 0

            pcall(function()
                local src = descendant.Source
                sourceLength = #src
                lineCount = select(2, src:gsub('\n', '\n')) + 1
            end)

            table.insert(scripts, {
                name = descendant.Name,
                path = descendant:GetFullName(),
                type = descendant.ClassName,
                size = sourceLength,
                lines = lineCount,
                enabled = descendant:IsA("ModuleScript") and "N/A" or tostring(descendant.Enabled)
            })

            count = count + 1
        end
    end

    table.sort(scripts, function(a, b)
        return a.size > b.size
    end)

    local report = "🔥 TOP 10 LARGEST SCRIPTS:\n\n"

    for i = 1, math.min(10, #scripts) do
        local script = scripts[i]
        report = report .. string.format("#%d %s [%s]\n", i, script.name, script.type)
        report = report .. string.format("   %d chars | %d lines\n", script.size, script.lines)
    end

    local totalSize = 0
    for _, script in ipairs(scripts) do
        totalSize = totalSize + script.size
    end

    report = report .. string.format("\n📊 Total: %d scripts | %d chars\n", #scripts, totalSize)

    return {
        success = true,
        report = report,
        stats = {
            total = #scripts,
            totalSize = totalSize
        }
    }
end

CommandHandlers.moduletracker = function(args)
    print("📦 Tracking ModuleScripts...")

    local modules = {}
    local count = 0
    local maxModules = 50

    for _, descendant in pairs(game:GetDescendants()) do
        if count >= maxModules then break end

        if descendant:IsA("ModuleScript") then
            local sourceLength = 0

            pcall(function()
                sourceLength = #descendant.Source
            end)

            table.insert(modules, {
                name = descendant.Name,
                path = descendant:GetFullName(),
                size = sourceLength
            })

            count = count + 1
        end
    end

    table.sort(modules, function(a, b)
        return a.size > b.size
    end)

    local report = "📦 MODULE SCRIPTS FOUND:\n\n"

    for i, module in ipairs(modules) do
        report = report .. string.format("[%d] %s\n", i, module.name)
        report = report .. string.format("    %d chars\n", module.size)
    end

    report = report .. string.format("\n📊 Total Modules: %d\n", #modules)

    return {
        success = true,
        report = report,
        stats = {
            total = #modules
        }
    }
end

CommandHandlers.flowwatch = function(args)
    local targetUser = args and args.user

    if not targetUser then
        return {
            success = false,
            error = "No target user specified"
        }
    end

    print("👁️ Starting FlowWatch for user: " .. targetUser)

    local targetPlayer = nil
    for _, player in pairs(game.Players:GetPlayers()) do
        if tostring(player.UserId) == targetUser or player.Name:lower() == targetUser:lower() then
            targetPlayer = player
            break
        end
    end

    if not targetPlayer then
        return {
            success = false,
            error = "Player not found: " .. targetUser
        }
    end

    local function captureState()
        local state = {}
        for _, descendant in pairs(game:GetDescendants()) do
            if descendant:IsA("Script") or descendant:IsA("LocalScript") or descendant:IsA("ModuleScript") or descendant:IsA("Folder") then
                state[descendant:GetFullName()] = {
                    class = descendant.ClassName,
                    parent = descendant.Parent and descendant.Parent:GetFullName() or "nil",
                    name = descendant.Name
                }
            end
        end
        return state
    end

    FlowWatchState = {
        initialState = captureState(),
        targetPlayer = targetPlayer.Name,
        targetUserId = targetPlayer.UserId,
        changes = {},
        active = true
    }

    FlowWatchActive = true

    spawn(function()
        while FlowWatchActive do
            wait(2)

            local currentState = captureState()
            local changes = {
                added = {},
                removed = {},
                moved = {},
                timestamp = os.time()
            }

            for path, data in pairs(currentState) do
                if not FlowWatchState.initialState[path] then
                    table.insert(changes.added, {
                        path = path,
                        name = data.name,
                        class = data.class,
                        parent = data.parent
                    })
                end
            end

            for path, data in pairs(FlowWatchState.initialState) do
                if not currentState[path] then
                    table.insert(changes.removed, {
                        path = path,
                        name = data.name,
                        class = data.class
                    })
                end
            end

            if #changes.added > 0 or #changes.removed > 0 then
                table.insert(FlowWatchState.changes, changes)
            end

            FlowWatchState.initialState = currentState
        end
    end)

    return {
        success = true,
        message = "FlowWatch started for " .. targetPlayer.Name,
        player = targetPlayer.Name,
        userId = targetPlayer.UserId
    }
end

CommandHandlers.flowwatch_poll = function(args)
    if not FlowWatchActive then
        return {
            success = false,
            error = "FlowWatch is not active"
        }
    end

    local pendingChanges = FlowWatchState.changes
    FlowWatchState.changes = {}

    return {
        success = true,
        active = FlowWatchActive,
        player = FlowWatchState.targetPlayer,
        changes = pendingChanges
    }
end

CommandHandlers.flowwatch_stop = function(args)
    FlowWatchActive = false
    FlowWatchState = {}

    return {
        success = true,
        message = "FlowWatch stopped"
    }
end

CommandHandlers.buildmap = function(args)
    print("🗺️ Building game map...")

    local function getInstanceDetails(instance, depth, maxDepth)
        depth = depth or 0
        maxDepth = maxDepth or 10

        if depth >= maxDepth then
            return nil
        end

        local details = {
            name = instance.Name,
            class = instance.ClassName,
            path = instance:GetFullName(),
            children = {}
        }

        pcall(function()
            if instance:IsA("Part") or instance:IsA("MeshPart") then
                details.size = tostring(instance.Size)
                details.position = tostring(instance.Position)
            end
        end)

        for _, child in pairs(instance:GetChildren()) do
            local childDetails = getInstanceDetails(child, depth + 1, maxDepth)
            if childDetails then
                table.insert(details.children, childDetails)
            end
        end

        return details
    end

    local function formatTree(node, indent, isLast)
        indent = indent or ""
        local output = ""

        local prefix = isLast and "└── " or "├── "
        local connector = isLast and "    " or "│   "

        local info = node.name .. " [" .. node.class .. "]"
        output = indent .. prefix .. info .. "\n"

        for i, child in ipairs(node.children) do
            local isLastChild = i == #node.children
            output = output .. formatTree(child, indent .. connector, isLastChild)
        end

        return output
    end

    local gameMap = {
        workspace = getInstanceDetails(game.Workspace, 0, 4),
        replicatedStorage = getInstanceDetails(game.ReplicatedStorage, 0, 4)
    }

    local treeText = "╔═══════════════════════════════════════╗\n"
    treeText = treeText .. "║        COMPLETE GAME MAP              ║\n"
    treeText = treeText .. "╚═══════════════════════════════════════╝\n\n"

    treeText = treeText .. "📂 Workspace\n"
    for i, child in ipairs(gameMap.workspace.children) do
        treeText = treeText .. formatTree(child, "", i == #gameMap.workspace.children)
    end

    return {
        success = true,
        tree = treeText,
        data = gameMap,
        stats = {
            totalInstances = #game:GetDescendants(),
            players = #Players:GetPlayers()
        }
    }
end

CommandHandlers.exe = function(args)
    local script = args and args.script

    if not script or script == "" then
        return {
            success = false,
            error = "No script provided"
        }
    end

    print("⚡ Executing script...")

    local success, err

    if script:match("^https?://") then
        success, err = pcall(function()
            loadstring(game:HttpGet(script, true))()
        end)
    else
        success, err = pcall(function()
            loadstring(script)()
        end)
    end

    if success then
        return {
            success = true,
            message = "Script executed successfully"
        }
    else
        return {
            success = false,
            error = tostring(err)
        }
    end
end

CommandHandlers.dex = function(args)
    if dexLoaded then
        return {
            success = false,
            error = "DEX is already running. Rejoin the game to launch it again."
        }
    end

    local revamp = args and args.revamp == true

    local dexUrl = "https://raw.githubusercontent.com/raelhubfunctions/Save-scripts/refs/heads/main/DexMobile.lua"
    local dexName = revamp and "DEX Mobile (Revamped)" or "Dark DEX Mobile"

    local success, err = pcall(function()
        loadstring(game:HttpGet(dexUrl, true))()
    end)

    if success then
        dexLoaded = true
        return {
            success = true,
            message = dexName .. " launched successfully"
        }
    else
        return {
            success = false,
            error = tostring(err)
        }
    end
end

-- Function to send command response
local function sendResponse(commandId, response, status)
    local success, result = pcall(function()
        local payload = HttpService:JSONEncode({
            command_id = commandId,
            response = response,
            status = status or "completed"
        })

        local httpResponse = request({
            Url = RESPONSE_ENDPOINT,
            Method = "POST",
            Headers = {
                ["Content-Type"] = "application/json",
                ["apikey"] = API_KEY,
                ["Authorization"] = "Bearer " .. API_KEY
            },
            Body = payload
        })

        return httpResponse.StatusCode == 200
    end)

    return success
end

-- Function to poll for commands
local function pollCommands()
    local success, result = pcall(function()
        local url = COMMANDS_ENDPOINT .. "?account_id=" .. ACCOUNT_ID
        local agentUrl = COMMANDS_ENDPOINT .. "?account_id=agent_" .. ACCOUNT_ID

        local commands = {}

        local response = request({
            Url = url,
            Method = "GET",
            Headers = {
                ["Content-Type"] = "application/json",
                ["apikey"] = API_KEY,
                ["Authorization"] = "Bearer " .. API_KEY
            }
        })

        if response.StatusCode == 200 then
            local data = HttpService:JSONDecode(response.Body)
            for _, cmd in ipairs(data.commands or {}) do
                table.insert(commands, cmd)
            end
        end

        local agentResponse = request({
            Url = agentUrl,
            Method = "GET",
            Headers = {
                ["Content-Type"] = "application/json",
                ["apikey"] = API_KEY,
                ["Authorization"] = "Bearer " .. API_KEY
            }
        })

        if agentResponse.StatusCode == 200 then
            local agentData = HttpService:JSONDecode(agentResponse.Body)
            for _, cmd in ipairs(agentData.commands or {}) do
                table.insert(commands, cmd)
            end
        end

        return commands
    end)

    if success and result then
        return result
    else
        return {}
    end
end

-- Function to execute command
local function executeCommand(cmd)
    local commandName = cmd.command
    local commandId = cmd.id
    local args = cmd.args or {}

    print("⚡ Executing command: " .. commandName)

    local handler = nil

    if commandName:match("^agent_") then
        handler = AgentCommands[commandName]
    else
        handler = CommandHandlers[commandName]
    end

    if handler then
        local success, result = pcall(function()
            return handler(args)
        end)

        if success then
            if result and result.success then
                sendResponse(commandId, result, "completed")
                print("✓ Command completed: " .. commandName)
            elseif result then
                sendResponse(commandId, result, "failed")
                warn("✗ Command failed: " .. commandName)
                warn("  Error: " .. tostring(result.error))
            else
                sendResponse(commandId, {error = "No result returned"}, "failed")
                warn("✗ Command returned no result: " .. commandName)
            end
        else
            sendResponse(commandId, {error = tostring(result)}, "failed")
            warn("✗ Command error: " .. tostring(result))
        end
    else
        sendResponse(commandId, {error = "Unknown command: " .. commandName}, "failed")
        warn("✗ Unknown command: " .. commandName)
    end
end

-- Main polling loop
local function startCommandListener()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("✓ Lumen Command Executor Active!")
    print("✓ Account ID: " .. ACCOUNT_ID)
    print("✓ Listening for commands...")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    spawn(function()
        while true do
            local commands = pollCommands()

            for _, cmd in ipairs(commands) do
                spawn(function()
                    executeCommand(cmd)
                end)
            end

            wait(2)
        end
    end)
end

-- Start the listener
startCommandListener()
