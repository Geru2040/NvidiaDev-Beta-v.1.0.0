-- Auto-generated GUI Script
local player = game.Players.LocalPlayer
local gui = player:WaitForChild('PlayerGui')

local o1 = Instance.new("ScreenGui")
o1.Enabled = true
o1.Name = "DoubleBarelAutoDraw"
o1.DisplayOrder = 999999999
o1.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
o1.Parent = gui

    local o2 = Instance.new("Frame")
    o2.Position = UDim2.new(0.306, 0.000, 0.282, 0.000)
    o2.Size = UDim2.new(0.000, 398.000, 0.000, 225.000)
    o2.AnchorPoint = Vector2.new(0.000, 0.000)
    o2.BackgroundColor3 = Color3.new(0.059, 0.067, 0.102)
    o2.BackgroundTransparency = 0
    o2.BorderColor3 = Color3.new(0.000, 0.000, 0.000)
    o2.BorderSizePixel = 0
    o2.LayoutOrder = 0
    o2.Rotation = 0
    o2.Visible = true
    o2.ZIndex = 1
    o2.ClipsDescendants = false
    o2.Active = false
    o2.Selectable = false
    o2.Transparency = 0
    o2.Name = "Frame"
    o2.Parent = o1

        local o3 = Instance.new("UICorner")
        o3.CornerRadius = UDim.new(0.000, 5.000)
        o3.Name = "UICorner"
        o3.Parent = o2

        local o4 = Instance.new("Frame")
        o4.Position = UDim2.new(0.010, 0.000, 0.170, 0.000)
        o4.Size = UDim2.new(0.000, 389.000, 0.000, 181.000)
        o4.AnchorPoint = Vector2.new(0.000, 0.000)
        o4.BackgroundColor3 = Color3.new(0.095, 0.108, 0.165)
        o4.BackgroundTransparency = 0
        o4.BorderColor3 = Color3.new(0.000, 0.000, 0.000)
        o4.BorderSizePixel = 0
        o4.LayoutOrder = 0
        o4.Rotation = 0
        o4.Visible = true
        o4.ZIndex = 1
        o4.ClipsDescendants = false
        o4.Active = false
        o4.Selectable = false
        o4.Transparency = 0
        o4.Name = "Frame"
        o4.Parent = o2

            local o5 = Instance.new("UICorner")
            o5.CornerRadius = UDim.new(0.000, 5.000)
            o5.Name = "UICorner"
            o5.Parent = o4

            local o6 = Instance.new("TextButton")
            o6.Position = UDim2.new(0.007, 0.000, 0.739, 0.000)
            o6.Size = UDim2.new(0.000, 383.000, 0.000, 41.000)
            o6.AnchorPoint = Vector2.new(0.000, 0.000)
            o6.BackgroundColor3 = Color3.new(0.188, 0.196, 0.318)
            o6.BackgroundTransparency = 0
            o6.BorderColor3 = Color3.new(0.000, 0.000, 0.000)
            o6.BorderSizePixel = 0
            o6.LayoutOrder = 0
            o6.Rotation = 0
            o6.Visible = true
            o6.ZIndex = 1
            o6.ClipsDescendants = false
            o6.Active = false
            o6.Selectable = false
            o6.Text = "Draw!"
            o6.TextColor3 = Color3.new(0.396, 0.620, 0.780)
            o6.TextSize = 27
            o6.Font = Enum.Font.SourceSansBold
            o6.TextXAlignment = Enum.TextXAlignment.Center
            o6.TextYAlignment = Enum.TextYAlignment.Center
            o6.TextScaled = false
            o6.TextWrapped = true
            o6.RichText = false
            o6.TextStrokeColor3 = Color3.new(0.000, 0.000, 0.000)
            o6.TextStrokeTransparency = 1
            o6.TextTransparency = 0
            o6.AutoButtonColor = true
            o6.Modal = false
            o6.Transparency = 0
            o6.Name = "SubmitDraw"
            o6.Parent = o4

                local o7 = Instance.new("UICorner")
                o7.CornerRadius = UDim.new(0.000, 5.000)
                o7.Name = "UICorner"
                o7.Parent = o6

            local o6a = Instance.new("TextButton")
            o6a.Position = UDim2.new(0.530, 0.000, 0.739, 0.000)
            o6a.Size = UDim2.new(0.000, 179.000, 0.000, 41.000)
            o6a.AnchorPoint = Vector2.new(0.000, 0.000)
            o6a.BackgroundColor3 = Color3.new(0.188, 0.196, 0.318)
            o6a.BackgroundTransparency = 0
            o6a.BorderColor3 = Color3.new(0.000, 0.000, 0.000)
            o6a.BorderSizePixel = 0
            o6a.LayoutOrder = 0
            o6a.Rotation = 0
            o6a.Visible = false
            o6a.ZIndex = 1
            o6a.ClipsDescendants = false
            o6a.Active = false
            o6a.Selectable = false
            o6a.Text = "Place"
            o6a.TextColor3 = Color3.new(0.396, 0.620, 0.780)
            o6a.TextSize = 27
            o6a.Font = Enum.Font.SourceSansBold
            o6a.TextXAlignment = Enum.TextXAlignment.Center
            o6a.TextYAlignment = Enum.TextYAlignment.Center
            o6a.TextScaled = false
            o6a.TextWrapped = true
            o6a.RichText = false
            o6a.TextStrokeColor3 = Color3.new(0.000, 0.000, 0.000)
            o6a.TextStrokeTransparency = 1
            o6a.TextTransparency = 0
            o6a.AutoButtonColor = true
            o6a.Modal = false
            o6a.Transparency = 0
            o6a.Name = "PlaceButton"
            o6a.Parent = o4

                local o7a = Instance.new("UICorner")
                o7a.CornerRadius = UDim.new(0.000, 5.000)
                o7a.Name = "UICorner"
                o7a.Parent = o6a

            local o8 = Instance.new("TextBox")
            o8.Position = UDim2.new(0.007, 0.000, 0.557, 0.000)
            o8.Size = UDim2.new(0.000, 383.000, 0.000, 27.000)
            o8.AnchorPoint = Vector2.new(0.000, 0.000)
            o8.BackgroundColor3 = Color3.new(0.082, 0.094, 0.145)
            o8.BackgroundTransparency = 0
            o8.BorderColor3 = Color3.new(0.000, 0.000, 0.000)
            o8.BorderSizePixel = 0
            o8.LayoutOrder = 0
            o8.Rotation = 0
            o8.Visible = true
            o8.ZIndex = 1
            o8.ClipsDescendants = false
            o8.Active = true
            o8.Selectable = true
            o8.Text = ""
            o8.TextColor3 = Color3.new(1.000, 1.000, 1.000)
            o8.TextSize = 17
            o8.Font = Enum.Font.Ubuntu
            o8.TextXAlignment = Enum.TextXAlignment.Center
            o8.TextYAlignment = Enum.TextYAlignment.Center
            o8.TextScaled = false
            o8.TextWrapped = true
            o8.RichText = false
            o8.TextStrokeColor3 = Color3.new(0.000, 0.000, 0.000)
            o8.TextStrokeTransparency = 1
            o8.TextTransparency = 0
            o8.Transparency = 0
            o8.PlaceholderColor3 = Color3.new(0.702, 0.702, 0.702)
            o8.PlaceholderText = "enter image url.."
            o8.ClearTextOnFocus = false
            o8.MultiLine = false
            o8.TextEditable = true
            o8.Name = "UrlInput"
            o8.Parent = o4

                local o9 = Instance.new("UICorner")
                o9.CornerRadius = UDim.new(0.000, 5.000)
                o9.Name = "UICorner"
                o9.Parent = o8

                local o10 = Instance.new("UIStroke")
                o10.ZIndex = 1
                o10.Color = Color3.new(0.133, 0.141, 0.227)
                o10.Thickness = 1
                o10.Transparency = 0
                o10.ApplyStrokeMode = Enum.ApplyStrokeMode.Border
                o10.LineJoinMode = Enum.LineJoinMode.Round
                o10.Enabled = true
                o10.Name = "UIStroke"
                o10.Parent = o8

            local MarketPlaceService = game:GetService("MarketplaceService")
            local gameName = "Unknown"
            pcall(function()
                gameName = MarketPlaceService:GetProductInfo(game.PlaceId).Name
            end)

            local o11 = Instance.new("TextLabel")
            o11.Position = UDim2.new(0.007, 0.000, 0.369, 0.000)
            o11.Size = UDim2.new(0.000, 200.000, 0.000, 28.000)
            o11.AnchorPoint = Vector2.new(0.000, 0.000)
            o11.BackgroundColor3 = Color3.new(0.188, 0.196, 0.318)
            o11.BackgroundTransparency = 0
            o11.BorderColor3 = Color3.new(0.000, 0.000, 0.000)
            o11.BorderSizePixel = 0
            o11.LayoutOrder = 0
            o11.Rotation = 0
            o11.Visible = true
            o11.ZIndex = 1
            o11.ClipsDescendants = false
            o11.Active = false
            o11.Selectable = false
            o11.Text = "Game: " .. gameName
            o11.TextColor3 = Color3.new(0.733, 0.835, 0.910)
            o11.TextSize = 17
            o11.Font = Enum.Font.SourceSansBold
            o11.TextXAlignment = Enum.TextXAlignment.Center
            o11.TextYAlignment = Enum.TextYAlignment.Center
            o11.TextScaled = false
            o11.TextWrapped = true
            o11.RichText = false
            o11.TextStrokeColor3 = Color3.new(0.000, 0.000, 0.000)
            o11.TextStrokeTransparency = 1
            o11.TextTransparency = 0
            o11.Transparency = 0
            o11.Name = "GameNameLabel"
            o11.Parent = o4

                local o12 = Instance.new("UICorner")
                o12.CornerRadius = UDim.new(0.000, 5.000)
                o12.Name = "UICorner"
                o12.Parent = o11

            local o13 = Instance.new("CanvasGroup")
            o13.Position = UDim2.new(0.000, 0.000, -0.177, 0.000)
            o13.Size = UDim2.new(0.000, 389.000, 0.000, 32.000)
            o13.AnchorPoint = Vector2.new(0.000, 0.000)
            o13.BackgroundColor3 = Color3.new(1.000, 1.000, 1.000)
            o13.BackgroundTransparency = 1
            o13.BorderColor3 = Color3.new(0.000, 0.000, 0.000)
            o13.BorderSizePixel = 0
            o13.LayoutOrder = 0
            o13.Rotation = 0
            o13.Visible = true
            o13.ZIndex = 2
            o13.ClipsDescendants = true
            o13.Active = false
            o13.Selectable = false
            o13.Transparency = 1
            o13.GroupColor3 = Color3.new(1.000, 1.000, 1.000)
            o13.GroupTransparency = 0
            o13.Name = "TopBar"
            o13.Parent = o4

                local o14 = Instance.new("Frame")
                o14.Position = UDim2.new(0.000, 0.000, 0.000, 0.000)
                o14.Size = UDim2.new(0.000, 389.000, 0.000, 24.000)
                o14.AnchorPoint = Vector2.new(0.000, 0.000)
                o14.BackgroundColor3 = Color3.new(0.087, 0.100, 0.149)
                o14.BackgroundTransparency = 0
                o14.BorderColor3 = Color3.new(0.095, 0.108, 0.165)
                o14.BorderSizePixel = 0
                o14.LayoutOrder = 0
                o14.Rotation = 0
                o14.Visible = true
                o14.ZIndex = 2
                o14.ClipsDescendants = false
                o14.Active = false
                o14.Selectable = false
                o14.Transparency = 0
                o14.Name = "Frame"
                o14.Parent = o13

                    local o15 = Instance.new("UICorner")
                    o15.CornerRadius = UDim.new(0.000, 3.000)
                    o15.Name = "UICorner"
                    o15.Parent = o14

                local o16 = Instance.new("Frame")
                o16.Position = UDim2.new(0.000, 0.000, 0.458, 0.000)
                o16.Size = UDim2.new(0.000, 389.000, 0.000, 12.000)
                o16.AnchorPoint = Vector2.new(0.000, 0.000)
                o16.BackgroundColor3 = Color3.new(0.087, 0.100, 0.149)
                o16.BackgroundTransparency = 0
                o16.BorderColor3 = Color3.new(0.095, 0.108, 0.165)
                o16.BorderSizePixel = 0
                o16.LayoutOrder = 0
                o16.Rotation = 0
                o16.Visible = true
                o16.ZIndex = 2
                o16.ClipsDescendants = false
                o16.Active = false
                o16.Selectable = false
                o16.Transparency = 0
                o16.Name = "Frame"
                o16.Parent = o13

                local o17 = Instance.new("TextLabel")
                o17.Position = UDim2.new(0.000, 0.000, 0.000, 0.000)
                o17.Size = UDim2.new(0.000, 81.000, 0.000, 25.000)
                o17.AnchorPoint = Vector2.new(0.000, 0.000)
                o17.BackgroundColor3 = Color3.new(1.000, 1.000, 1.000)
                o17.BackgroundTransparency = 1
                o17.BorderColor3 = Color3.new(0.000, 0.000, 0.000)
                o17.BorderSizePixel = 0
                o17.LayoutOrder = 0
                o17.Rotation = 0
                o17.Visible = true
                o17.ZIndex = 5
                o17.ClipsDescendants = false
                o17.Active = false
                o17.Selectable = false
                o17.Text = "DoubleBarel"
                o17.TextColor3 = Color3.new(0.682, 0.776, 0.855)
                o17.TextSize = 14
                o17.Font = Enum.Font.SourceSansBold
                o17.TextXAlignment = Enum.TextXAlignment.Center
                o17.TextYAlignment = Enum.TextYAlignment.Center
                o17.TextScaled = false
                o17.TextWrapped = false
                o17.RichText = false
                o17.TextStrokeColor3 = Color3.new(0.000, 0.000, 0.000)
                o17.TextStrokeTransparency = 1
                o17.TextTransparency = 0
                o17.Name = "TextBox"
                o17.Parent = o13

                local o18 = Instance.new("TextLabel")
                o18.Position = UDim2.new(0.208, 0.000, 0.150, 0.000)
                o18.Size = UDim2.new(0.000, 70.000, 0.000, 18.000)
                o18.AnchorPoint = Vector2.new(0.000, 0.000)
                o18.BackgroundColor3 = Color3.new(0.188, 0.196, 0.318)
                o18.BackgroundTransparency = 0
                o18.BorderColor3 = Color3.new(0.000, 0.000, 0.000)
                o18.BorderSizePixel = 0
                o18.LayoutOrder = 0
                o18.Rotation = 0
                o18.Visible = true
                o18.ZIndex = 5
                o18.ClipsDescendants = false
                o18.Active = false
                o18.Selectable = false
                o18.Text = "Paid"
                o18.TextColor3 = Color3.new(0.682, 0.776, 0.855)
                o18.TextSize = 14
                o18.Font = Enum.Font.SourceSansBold
                o18.TextXAlignment = Enum.TextXAlignment.Center
                o18.TextYAlignment = Enum.TextYAlignment.Center
                o18.TextScaled = false
                o18.TextWrapped = false
                o18.RichText = false
                o18.TextStrokeColor3 = Color3.new(0.000, 0.000, 0.000)
                o18.TextStrokeTransparency = 1
                o18.TextTransparency = 0
                o18.Transparency = 0
                o18.Name = "TextBox"
                o18.Parent = o13

                    local o19 = Instance.new("UICorner")
                    o19.CornerRadius = UDim.new(0.000, 3.000)
                    o19.Name = "UICorner"
                    o19.Parent = o18

                local o18a = Instance.new("TextLabel")
                o18a.Position = UDim2.new(0.395, 0.000, 0.150, 0.000)
                o18a.Size = UDim2.new(0, 0, 0, 18)
                o18a.AnchorPoint = Vector2.new(0.000, 0.000)
                o18a.BackgroundColor3 = Color3.new(0.188, 0.196, 0.318)
                o18a.BackgroundTransparency = 0
                o18a.BorderColor3 = Color3.new(0.000, 0.000, 0.000)
                o18a.BorderSizePixel = 0
                o18a.LayoutOrder = 0
                o18a.Rotation = 0
                o18a.Visible = true
                o18a.ZIndex = 5
                o18a.ClipsDescendants = false
                o18a.Active = false
                o18a.Selectable = false
                o18a.Text = "Game: Supported"
                o18a.TextColor3 = Color3.new(0.682, 0.776, 0.855)
                o18a.TextSize = 14
                o18a.Font = Enum.Font.SourceSansBold
                o18a.TextXAlignment = Enum.TextXAlignment.Center
                o18a.TextYAlignment = Enum.TextYAlignment.Center
                o18a.TextScaled = false
                o18a.TextWrapped = false
                o18a.RichText = true
                o18a.AutomaticSize = Enum.AutomaticSize.X
                o18a.TextStrokeColor3 = Color3.new(0.000, 0.000, 0.000)
                o18a.TextStrokeTransparency = 1
                o18a.TextTransparency = 0
                o18a.Transparency = 0
                o18a.Name = "GameStatus"
                o18a.Parent = o13

                    local o19a = Instance.new("UICorner")
                    o19a.CornerRadius = UDim.new(0.000, 3.000)
                    o19a.Name = "UICorner"
                    o19a.Parent = o18a

                    local o19b = Instance.new("UIPadding")
                    o19b.PaddingLeft = UDim.new(0, 8)
                    o19b.PaddingRight = UDim.new(0, 8)
                    o19b.Name = "UIPadding"
                    o19b.Parent = o18a

                local o20 = Instance.new("TextButton")
                o20.Position = UDim2.new(0.884, 0.000, 0.094, 0.000)
                o20.Size = UDim2.new(0.000, 17.000, 0.000, 18.000)
                o20.AnchorPoint = Vector2.new(0.000, 0.000)
                o20.BackgroundColor3 = Color3.new(0.188, 0.196, 0.318)
                o20.BackgroundTransparency = 1
                o20.BorderColor3 = Color3.new(0.000, 0.000, 0.000)
                o20.BorderSizePixel = 0
                o20.LayoutOrder = 0
                o20.Rotation = 0
                o20.Visible = true
                o20.ZIndex = 5
                o20.ClipsDescendants = false
                o20.Active = true
                o20.Selectable = true
                o20.Text = "x"
                o20.TextColor3 = Color3.new(0.682, 0.776, 0.855)
                o20.TextSize = 14
                o20.Font = Enum.Font.SourceSansBold
                o20.TextXAlignment = Enum.TextXAlignment.Center
                o20.TextYAlignment = Enum.TextYAlignment.Center
                o20.TextScaled = false
                o20.TextWrapped = false
                o20.RichText = false
                o20.TextStrokeColor3 = Color3.new(0.000, 0.000, 0.000)
                o20.TextStrokeTransparency = 1
                o20.TextTransparency = 0
                o20.AutoButtonColor = true
                o20.Modal = false
                o20.Name = "CloseButton"
                o20.Parent = o13

                    local o21 = Instance.new("UICorner")
                    o21.CornerRadius = UDim.new(0.000, 3.000)
                    o21.Name = "UICorner"
                    o21.Parent = o20

                local o22 = Instance.new("TextButton")
                o22.Position = UDim2.new(0.928, 0.000, 0.094, 0.000)
                o22.Size = UDim2.new(0.000, 17.000, 0.000, 18.000)
                o22.AnchorPoint = Vector2.new(0.000, 0.000)
                o22.BackgroundColor3 = Color3.new(0.188, 0.196, 0.318)
                o22.BackgroundTransparency = 1
                o22.BorderColor3 = Color3.new(0.000, 0.000, 0.000)
                o22.BorderSizePixel = 0
                o22.LayoutOrder = 0
                o22.Rotation = 0
                o22.Visible = true
                o22.ZIndex = 5
                o22.ClipsDescendants = false
                o22.Active = true
                o22.Selectable = true
                o22.Text = "-"
                o22.TextColor3 = Color3.new(0.682, 0.776, 0.855)
                o22.TextSize = 14
                o22.Font = Enum.Font.SourceSansBold
                o22.TextXAlignment = Enum.TextXAlignment.Center
                o22.TextYAlignment = Enum.TextYAlignment.Center
                o22.TextScaled = false
                o22.TextWrapped = false
                o22.RichText = false
                o22.TextStrokeColor3 = Color3.new(0.000, 0.000, 0.000)
                o22.TextStrokeTransparency = 1
                o22.TextTransparency = 0
                o22.AutoButtonColor = true
                o22.Modal = false
                o22.Name = "MinimizeButton"
                o22.Parent = o13

                    local o23 = Instance.new("UICorner")
                    o23.CornerRadius = UDim.new(0.000, 3.000)
                    o23.Name = "UICorner"
                    o23.Parent = o22

            local o24 = Instance.new("TextLabel")
            o24.Position = UDim2.new(0.010, 0.000, 0.020, 0.000)
            o24.Size = UDim2.new(0.000, 382.000, 0.000, 54.000)
            o24.AnchorPoint = Vector2.new(0.000, 0.000)
            o24.BackgroundColor3 = Color3.new(0.188, 0.196, 0.318)
            o24.BackgroundTransparency = 0
            o24.BorderColor3 = Color3.new(0.000, 0.000, 0.000)
            o24.BorderSizePixel = 0
            o24.LayoutOrder = 0
            o24.Rotation = 0
            o24.Visible = true
            o24.ZIndex = 1
            o24.ClipsDescendants = false
            o24.Active = false
            o24.Selectable = false
            o24.Text = "URL REQUIREMENTS\n• Direct image links only (.png, .jpg, .gif)\n• Google Images redirect URLs will not work\n• Avoid HTML pages or embedded content"
            o24.TextColor3 = Color3.new(0.678, 0.769, 0.843)
            o24.TextSize = 13
            o24.Font = Enum.Font.SourceSansSemibold
            o24.TextXAlignment = Enum.TextXAlignment.Left
            o24.TextYAlignment = Enum.TextYAlignment.Top
            o24.TextScaled = false
            o24.TextWrapped = true
            o24.RichText = false
            o24.TextStrokeColor3 = Color3.new(0.000, 0.000, 0.000)
            o24.TextStrokeTransparency = 1
            o24.TextTransparency = 0
            o24.Transparency = 0
            o24.Name = "Readme.md"
            o24.Parent = o4

                local o25 = Instance.new("UICorner")
                o25.CornerRadius = UDim.new(0.000, 4.000)
                o25.Name = "UICorner"
                o25.Parent = o24

                local o25a = Instance.new("UIPadding")
                o25a.PaddingLeft = UDim.new(0, 8)
                o25a.PaddingRight = UDim.new(0, 8)
                o25a.PaddingTop = UDim.new(0, 6)
                o25a.PaddingBottom = UDim.new(0, 6)
                o25a.Parent = o24

            local o26 = Instance.new("Frame")
            o26.Position = UDim2.new(0.010, 0.000, 0.340, 0.000)
            o26.Size = UDim2.new(0.000, 381.000, 0.000, 2.000)
            o26.AnchorPoint = Vector2.new(0.000, 0.000)
            o26.BackgroundColor3 = Color3.new(0.188, 0.196, 0.318)
            o26.BackgroundTransparency = 0
            o26.BorderColor3 = Color3.new(0.000, 0.000, 0.000)
            o26.BorderSizePixel = 0
            o26.LayoutOrder = 0
            o26.Rotation = 0
            o26.Visible = true
            o26.ZIndex = 1
            o26.ClipsDescendants = false
            o26.Active = false
            o26.Selectable = false
            o26.Transparency = 0
            o26.Name = "detail"
            o26.Parent = o4

                local o27 = Instance.new("UIGradient")
                o27.Rotation = 0
                o27.Transparency = NumberSequence.new({
                    NumberSequenceKeypoint.new(0, 1),
                    NumberSequenceKeypoint.new(0.1, 0),
                    NumberSequenceKeypoint.new(0.9, 0),
                    NumberSequenceKeypoint.new(1, 1)
                })
                o27.Enabled = true
                o27.Offset = Vector2.new(0.000, 0.000)
                o27.Name = "UIGradient"
                o27.Parent = o26

            local o28 = Instance.new("TextButton")
            o28.Position = UDim2.new(0.530, 0.000, 0.369, 0.000)
            o28.Size = UDim2.new(0.000, 179.000, 0.000, 28.000)
            o28.AnchorPoint = Vector2.new(0.000, 0.000)
            o28.BackgroundColor3 = Color3.new(0.188, 0.196, 0.318)
            o28.BackgroundTransparency = 0
            o28.BorderColor3 = Color3.new(0.000, 0.000, 0.000)
            o28.BorderSizePixel = 0
            o28.LayoutOrder = 0
            o28.Rotation = 0
            o28.Visible = true
            o28.ZIndex = 1
            o28.ClipsDescendants = false
            o28.Active = false
            o28.Selectable = false
            o28.Text = "<font color='#BBCBE8'>Status:</font> <font color='#A0B5D0'>Loading...</font>"
            o28.TextColor3 = Color3.new(0.733, 0.835, 0.910)
            o28.TextSize = 17
            o28.Font = Enum.Font.SourceSans
            o28.TextXAlignment = Enum.TextXAlignment.Center
            o28.TextYAlignment = Enum.TextYAlignment.Center
            o28.TextScaled = false
            o28.TextWrapped = true
            o28.RichText = true
            o28.TextStrokeColor3 = Color3.new(0.000, 0.000, 0.000)
            o28.TextStrokeTransparency = 1
            o28.TextTransparency = 0
            o28.AutoButtonColor = true
            o28.Modal = false
            o28.Transparency = 0
            o28.Name = "StatusButton"
            o28.Parent = o4

                local o29 = Instance.new("UICorner")
                o29.CornerRadius = UDim.new(0.000, 5.000)
                o29.Name = "UICorner"
                o29.Parent = o28

-- Status API Integration
local HttpService = game:GetService("HttpService")
local TweenService = game:GetService("TweenService")
local statusButton = o28
local drawButton = o6
local placeButton = o6a
local urlInput = o8
local urlStroke = o10
local closeButton = o20
local minimizeButton = o22
local gameStatus = o18a

local speedBoostEnabled = false

-- Check if Place button should be visible
if game.PlaceId == 5991163185 then
    drawButton.Size = UDim2.new(0, 200, 0, 41)
    placeButton.Visible = true
else
    drawButton.Size = UDim2.new(0, 383, 0, 41)
    placeButton.Visible = false
end

-- Check if game is supported
local supportedGames = {
    [7074772062] = true,
    [5991163185] = true
}

local currentGameId = game.PlaceId
gameStatus.Text = "<font color='#AECBDB'>Game:</font> <font color='#93C47D'>Supported</font>"

-- Print welcome message
print("\n" .. string.rep("=", 60))
print("🔥 Thanks for buying DoubleBarel @" .. player.Name .. ", enjoy! 🔥")
print(string.rep("=", 60) .. "\n")

local statusColors = {
    Optimal = "#6FA8DC",
    Operational = "#93C47D",
    Degraded = "#E06666"
}

local function updateStatus()
    local requestFunc = request or http_request or syn and syn.request

    if requestFunc then
        local success, response = pcall(function()
            return requestFunc({
                Url = "https://bljvywddqbnllkrsvazb.supabase.co/functions/v1/status",
                Method = "GET"
            })
        end)

        if success and response.StatusCode == 200 then
            local data = HttpService:JSONDecode(response.Body)
            local status = data.status or "N/A"
            local color = statusColors[status] or "#A0B5D0"
            statusButton.Text = string.format("<font color='#BBCBE8'>Status:</font> <font color='%s'>%s</font>", color, status)
        else
            statusButton.Text = "<font color='#BBCBE8'>Status:</font> <font color='#E06666'>Error</font>"
        end
    else
        local success, response = pcall(function()
            return HttpService:GetAsync("https://bljvywddqbnllkrsvazb.supabase.co/functions/v1/status")
        end)

        if success then
            local data = HttpService:JSONDecode(response)
            local status = data.status or "N/A"
            local color = statusColors[status] or "#A0B5D0"
            statusButton.Text = string.format("<font color='#BBCBE8'>Status:</font> <font color='%s'>%s</font>", color, status)
        else
            statusButton.Text = "<font color='#BBCBE8'>Status:</font> <font color='#E06666'>No Connection</font>"
        end
    end
end

task.spawn(function()
    updateStatus()
    while task.wait(30) do
        updateStatus()
    end
end)

-- Clear Canvas functionality removed as requested
-- ID Label logic handled during initialization

-- ============================================================================
-- UNIVERSAL DRAWING SCRIPT INTEGRATION
-- ============================================================================
local FETCH_SIZE = 2200
local ROTATION = 0
local AUTO_RESTORE = true

local pixelBuffer = nil
local canvasWidth = nil
local canvasHeight = nil
local targetImage = nil
local imageLoaded = false

-- Universal canvas detection
local function findCanvas()
    local playerGui = player:WaitForChild("PlayerGui")
    -- Try specific game structure (Menus > Drawing path)
    local drawingMenu = playerGui:FindFirstChild("Menus")
    if drawingMenu then
        local drawing = drawingMenu:FindFirstChild("Drawing")
        if drawing then
            local drawingContainer = drawing:FindFirstChild("Drawing")
            if drawingContainer then
                local container = drawingContainer:FindFirstChild("Drawing")
                if container then
                    local canvasFrame = container:FindFirstChild("Canvas")
                    if canvasFrame then
                        local canvas = canvasFrame:FindFirstChild("Canvas")
                        if canvas and canvas:IsA("ImageLabel") then
                            if canvas.ImageContent and canvas.ImageContent.SourceType == Enum.ContentSourceType.Object then
                                local editableImage = canvas.ImageContent.Object
                                if editableImage and editableImage:IsA("EditableImage") then
                                    return editableImage, canvas, "editableimage"
                                end
                            end
                        end
                    end
                end
                
                -- New Method (Container/Canvas/Canvas structure)
                local container2 = drawingContainer:FindFirstChild("Container")
                if container2 then
                    local canvasFrame2 = container2:FindFirstChild("Canvas")
                    if canvasFrame2 then
                        local canvas2 = canvasFrame2:FindFirstChild("Canvas")
                        if canvas2 and canvas2:IsA("ImageLabel") then
                            if canvas2.ImageContent and canvas2.ImageContent.SourceType == Enum.ContentSourceType.Object then
                                local editableImage2 = canvas2.ImageContent.Object
                                if editableImage2 and editableImage2:IsA("EditableImage") then
                                    -- Add epsilon offset for pixel-perfect alignment in new method
                                    return editableImage2, canvas2, "editableimage"
                                end
                            end
                        end
                    end
                end
            end
        end
    end

    -- Try Layers library method (for games using DrawingHandler)
    local success, Layers = pcall(function()
        return require(player.PlayerScripts.Libraries.DrawingHandler.Layers)
    end)
    if success and Layers then
        local canvas = Layers.GetCurrentCanvas()
        if canvas and canvas.InternalCanvas then
            return canvas.InternalCanvas, canvas, "internalcanvas"
        end
    end

    -- Fallback: search all descendants
    for _, gui in ipairs(playerGui:GetDescendants()) do
        if gui:IsA("ImageLabel") and gui.Visible then
            if gui.ImageContent and gui.ImageContent.SourceType == Enum.ContentSourceType.Object then
                local editableImage = gui.ImageContent.Object
                if editableImage and editableImage:IsA("EditableImage") then
                    local size = editableImage.Size
                    -- Filter: canvas must be reasonable size (100x100 minimum)
                    if size.X >= 100 and size.Y >= 100 and size.X <= 2048 and size.Y <= 2048 then
                        -- Skip tiny UI elements and very large backgrounds
                        local absSize = gui.AbsoluteSize
                        if absSize.X >= 100 and absSize.Y >= 100 then
                            return editableImage, gui, "editableimage"
                        end
                    end
                end
            end
        end
    end
    return nil, nil, nil
end

-- Redraw from buffer
local function redraw()
    if not targetImage or not pixelBuffer then return end
    pcall(function()
        targetImage:WritePixelsBuffer(Vector2.zero, Vector2.new(canvasWidth, canvasHeight), pixelBuffer)
    end)
end

-- Install auto-restore system (works for all games)
local function setupAutoRestore(canvasLabel)
    if not AUTO_RESTORE then return end

    local isDrawing = false

    -- Find all possible input frames (parent, grandparent, etc.)
    local function findInputFrames(element)
        local frames = {}
        local current = element
        local depth = 0

        while current and depth < 5 do
            if current:IsA("GuiObject") then
                table.insert(frames, current)
            end
            current = current.Parent
            depth = depth + 1
        end

        return frames
    end

    local inputFrames = findInputFrames(canvasLabel)

    -- Connect to all possible input frames
    for _, frame in ipairs(inputFrames) do
        frame.InputBegan:Connect(function(input)
            if input.UserInputType == Enum.UserInputType.MouseButton1 or 
               input.UserInputType == Enum.UserInputType.Touch then
                isDrawing = true
            end
        end)

        frame.InputEnded:Connect(function(input)
            if input.UserInputType == Enum.UserInputType.MouseButton1 or 
               input.UserInputType == Enum.UserInputType.Touch then
                if isDrawing and imageLoaded and targetImage then
                    isDrawing = false
                    task.wait(0.05)
                    redraw()
                end
            end
        end)
    end

    -- Also monitor canvas changes directly (for games that clear the canvas)
    task.spawn(function()
        while true do
            task.wait(0.1)
            -- If user is not actively drawing, ensure image is there
            -- ONLY restore if we are currently in an active round
            if imageLoaded and targetImage and not isDrawing and IN_ROUND then
                redraw()
            end
        end
    end)
end

-- Main drawing function
local function draw()
    local canvas, canvasLabel, canvasType = findCanvas()
    if not canvas then return end

    local originalButtonText = drawButton.Text
    drawButton.Text = "Drawing.."

    targetImage = canvas

    if canvasType == "internalcanvas" then
        canvasWidth = canvas.Width
        canvasHeight = canvas.Height
    else
        local size = canvas.Size
        canvasWidth = size.X
        canvasHeight = size.Y
    end

    -- Use 270 degree rotation for InternalCanvas games, 0 for others
    local rotationToUse = canvasType == "internalcanvas" and 270 or ROTATION

    local IMAGE_URL = urlInput.Text:gsub("^%s*(.-)%s*$", "%1")

    local response = (syn and syn.request or http_request or request)({
        Url = "https://bljvywddqbnllkrsvazb.supabase.co/functions/v1/pixelart",
        Method = "POST",
        Headers = {["Content-Type"] = "application/json"},
        Body = HttpService:JSONEncode({
            imageUrl = IMAGE_URL,
            size = FETCH_SIZE,
            rotation = rotationToUse
        })
    })

    if response.StatusCode ~= 200 then 
        drawButton.Text = originalButtonText
        return 
    end

    local data = HttpService:JSONDecode(response.Body)
    local pixels = data.pixels
    local imageWidth = data.width or FETCH_SIZE
    local imageHeight = data.height or FETCH_SIZE

    local bufferSize = canvasWidth * canvasHeight * 4
    pixelBuffer = buffer.create(bufferSize)

    -- White background (only for EditableImage type)
    if canvasType == "editableimage" then
        for i = 0, bufferSize - 1, 4 do
            buffer.writeu8(pixelBuffer, i, 255)
            buffer.writeu8(pixelBuffer, i + 1, 255)
            buffer.writeu8(pixelBuffer, i + 2, 255)
            buffer.writeu8(pixelBuffer, i + 3, 255)
        end
    elseif canvasType == "internalcanvas" then
        -- Clear InternalCanvas to white
        for x = 1, canvasWidth do
            for y = 1, canvasHeight do
                pcall(function()
                    canvas:SetRGBA(x, y, 1, 1, 1, 1)
                end)
            end
        end
        if canvasLabel then
            canvasLabel:Render()
        end
    end

    -- Scale and draw
    local scaleX = canvasWidth / imageWidth
    local scaleY = canvasHeight / imageHeight
    local scale = math.min(scaleX, scaleY)

    if canvasType == "internalcanvas" then
        -- Use SetRGBA with float values (0.0-1.0)
        -- Note: coordinates are already correct from API (no rotation needed)
        for i, hexColor in ipairs(pixels) do
            local srcX = (i - 1) % imageWidth
            local srcY = math.floor((i - 1) / imageWidth)

            -- Direct 1:1 mapping without additional rotation
            local canvasX = math.floor(srcX * scale + 0.001) + 1
            local canvasY = math.floor(srcY * scale + 0.001) + 1

            if canvasX >= 1 and canvasX <= canvasWidth and canvasY >= 1 and canvasY <= canvasHeight then
                local color = Color3.fromHex(hexColor)
                pcall(function()
                    canvas:SetRGBA(canvasX, canvasY, color.R, color.G, color.B, 1)
                end)
            end
        end

        if canvasLabel then
            canvasLabel:Render()
        end
    else
        -- Use buffer with byte values (0-255)
        for i, hexColor in ipairs(pixels) do
            local srcX = (i - 1) % imageWidth
            local srcY = math.floor((i - 1) / imageWidth)

            local canvasX = math.floor(srcX * scale + 0.001)
            local canvasY = math.floor(srcY * scale + 0.001)

            if canvasX >= 0 and canvasX < canvasWidth and canvasY >= 0 and canvasY < canvasHeight then
                local color = Color3.fromHex(hexColor)
                local idx = (canvasY * canvasWidth + canvasX) * 4

                buffer.writeu8(pixelBuffer, idx, math.floor(color.R * 255))
                buffer.writeu8(pixelBuffer, idx + 1, math.floor(color.G * 255))
                buffer.writeu8(pixelBuffer, idx + 2, math.floor(color.B * 255))
                buffer.writeu8(pixelBuffer, idx + 3, 255)
            end
        end

        pcall(function()
            canvas:WritePixelsBuffer(Vector2.zero, Vector2.new(canvasWidth, canvasHeight), pixelBuffer)
        end)
    end

    imageLoaded = true
    if canvasType == "editableimage" then
        setupAutoRestore(canvasLabel)
    end
    drawButton.Text = originalButtonText
end

-- Draw button functionality
drawButton.MouseButton1Click:Connect(function()
    local url = urlInput.Text:gsub("^%s*(.-)%s*$", "%1")

    if url == "" then
        local originalColor = urlInput.PlaceholderColor3
        urlInput.PlaceholderText = "Please enter URL first!"
        urlInput.PlaceholderColor3 = Color3.fromRGB(224, 102, 102)

        task.wait(1)
        urlInput.PlaceholderText = "enter image url.."
        urlInput.PlaceholderColor3 = originalColor
        return
    end

    AUTO_RESTORE = true
    draw()
end)

-- Close button
closeButton.MouseButton1Click:Connect(function()
    o1:Destroy()
end)

-- Drag functionality
local UIS = game:GetService("UserInputService")
local dragging, dragInput, dragStart, startPos

local function update(input)
    local delta = input.Position - dragStart
    o2.Position = UDim2.new(startPos.X.Scale, startPos.X.Offset + delta.X, startPos.Y.Scale, startPos.Y.Offset + delta.Y)
end

o13.InputBegan:Connect(function(input)
    if input.UserInputType == Enum.UserInputType.MouseButton1 or input.UserInputType == Enum.UserInputType.Touch then
        dragging = true
        dragStart = input.Position
        startPos = o2.Position

        input.Changed:Connect(function()
            if input.UserInputState == Enum.UserInputState.End then
                dragging = false
            end
        end)
    end
end)

o13.InputChanged:Connect(function(input)
    if input.UserInputType == Enum.UserInputType.MouseMovement or input.UserInputType == Enum.UserInputType.Touch then
        dragInput = input
    end
end)

UIS.InputChanged:Connect(function(input)
    if input == dragInput and dragging then
        update(input)
    end
end)

-- Gartic Phone Round Detector (FINAL) -- No GUI, no scanning, no guessing
local Players = game:GetService("Players")
local player = Players.LocalPlayer
local IN_ROUND = false
local lastTimerTick = 0
local hasDrawnThisRound = false
local ManaRemote = game:GetService("ReplicatedStorage")
    :WaitForChild("Signals")
    :WaitForChild("Mana")
    :WaitForChild("ManaRemoteEvent")

local function garticDraw()
    if hasDrawnThisRound then return end
    hasDrawnThisRound = true
    draw()
end

ManaRemote.OnClientEvent:Connect(function(path, value)
    -- Detect drawing timer updates
    if typeof(path) == "string" and path:find("DrawMe/Players/Player<" .. player.Name .. ">/Settings/DrawingTimer") and typeof(value) == "number" then
        lastTimerTick = os.clock()
        if not IN_ROUND then
            IN_ROUND = true
            hasDrawnThisRound = false -- Reset here to ensure fresh round
            imageLoaded = false -- Clear old image state
            pixelBuffer = nil -- Clear old pixel buffer
            print("🟢 ROUND STARTED")
            
            -- Auto clear canvas by painting it full white
            local canvas, canvasLabel, canvasType = findCanvas()
            if canvas then
                if canvasType == "editableimage" then
                    canvas:Clear(Color3.new(1, 1, 1), 1)
                elseif canvasType == "internalcanvas" then
                    for x = 1, canvas.Width do
                        for y = 1, canvas.Height do
                            pcall(function()
                                canvas:SetRGBA(x, y, 1, 1, 1, 1)
                            end)
                        end
                    end
                    if canvasLabel then
                        canvasLabel:Render()
                    end
                end
            end
            
            AUTO_RESTORE = true
            task.wait(0.5)
            garticDraw()
        end
    end
end)

-- watchdog: if timer stops, round ended
task.spawn(function()
    while true do
        task.wait(1)
        local timeSinceLastTick = os.clock() - lastTimerTick
        
        if IN_ROUND and timeSinceLastTick > 4.5 then -- Increased to 4.5s to absolutely avoid double state triggering
            IN_ROUND = false
            hasDrawnThisRound = false
            print("🔴 ROUND ENDED")
            AUTO_RESTORE = false
        end
    end
end)

-- Check if already in round on execution
local function checkInitialRound()
    task.wait(0.5)
    if os.clock() - lastTimerTick < 2 then
        IN_ROUND = true
        print("🟢 ALREADY IN ROUND")
        garticDraw()
    end
end

-- optional global getter
getgenv().IsInRound = function() return IN_ROUND end

print("DoubleBarel Auto Draw loaded!")
checkInitialRound()
print("\n" .. string.rep("=", 60))
print("🔥 Thanks for buying DoubleBarel @" .. player.Name .. ", enjoy! 🔥")
print(string.rep("=", 60) .. "\n")
