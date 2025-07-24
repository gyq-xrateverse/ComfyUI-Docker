@echo off
chcp 65001
setlocal enabledelayedexpansion

:: 定义仓库列表
set "REPOS[0]=https://github.com/Comfy-Org/ComfyUI-Manager.git"
set "REPOS[1]=https://github.com/kijai/ComfyUI-WanVideoWrapper.git"
set "REPOS[2]=https://github.com/kijai/ComfyUI-KJNodes.git"
set "REPOS[3]=https://github.com/cubiq/ComfyUI_essentials.git"
set "REPOS[4]=https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git"
set "REPOS[5]=https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes.git"
set "REPOS[6]=https://github.com/rgthree/rgthree-comfy.git"
set "REPOS[7]=https://github.com/crystian/ComfyUI-Crystools.git"
set "REPOS[8]=https://github.com/cubiq/ComfyUI_FaceAnalysis.git"
set "REPOS[9]=https://github.com/cubiq/ComfyUI_InstantID.git"
set "REPOS[10]=https://github.com/cubiq/PuLID_ComfyUI.git"
set "REPOS[11]=https://github.com/Fannovel16/comfyui_controlnet_aux.git"
set "REPOS[12]=https://github.com/Fannovel16/ComfyUI-Frame-Interpolation.git"
set "REPOS[13]=https://github.com/FizzleDorf/ComfyUI_FizzNodes.git"
set "REPOS[14]=https://github.com/Gourieff/ComfyUI-ReActor.git"
set "REPOS[15]=https://github.com/huchenlei/ComfyUI-layerdiffuse.git"
set "REPOS[16]=https://github.com/jags111/efficiency-nodes-comfyui.git"
set "REPOS[17]=https://github.com/ltdrdata/ComfyUI-Impact-Pack.git"
set "REPOS[18]=https://github.com/ltdrdata/ComfyUI-Impact-Subpack.git"
set "REPOS[19]=https://github.com/ltdrdata/ComfyUI-Inspire-Pack.git"
set "REPOS[20]=https://github.com/melMass/comfy_mtb.git"
set "REPOS[21]=https://github.com/storyicon/comfyui_segment_anything.git"
set "REPOS[22]=https://github.com/WASasquatch/was-node-suite-comfyui.git"
set "REPOS[23]=https://github.com/chflame163/ComfyUI_LayerStyle.git"
set "REPOS[24]=https://github.com/chflame163/ComfyUI_LayerStyle_Advance.git"
set "REPOS[25]=https://github.com/shadowcz007/comfyui-mixlab-nodes.git"
set "REPOS[26]=https://github.com/yolain/ComfyUI-Easy-Use.git"
set "REPOS[27]=https://github.com/kijai/ComfyUI-IC-Light.git"
set "REPOS[28]=https://github.com/siliconflow/BizyAir.git"
set "REPOS[29]=https://github.com/lquesada/ComfyUI-Inpaint-CropAndStitch.git"
set "REPOS[30]=https://github.com/lldacing/comfyui-easyapi-nodes.git"
set "REPOS[31]=https://github.com/kijai/ComfyUI-FluxTrainer.git"
set "REPOS[32]=https://github.com/kijai/ComfyUI-SUPIR.git"
set "REPOS[33]=https://github.com/MrForExample/ComfyUI-3D-Pack.git"
set "REPOS[34]=https://github.com/alt-key-project/comfyui-dream-video-batches.git"
set "REPOS[35]=https://github.com/nunchaku-tech/ComfyUI-nunchaku.git"
set "REPOS[36]=https://github.com/Dontdrunk/ComfyUI-DD-Translation.git"
set "REPOS[37]=https://github.com/AlekPet/ComfyUI_Custom_Nodes_AlekPet.git"
set "REPOS[38]=https://github.com/TTPlanetPig/Comfyui_TTP_Toolset.git"
set "REPOS[39]=https://github.com/ZenAI-Vietnam/ComfyUI-Kontext-Inpainting.git"
set "REPOS[40]=https://github.com/EvilBT/ComfyUI_SLK_joy_caption_two.git"
set "REPOS[41]=https://github.com/ShmuelRonen/ComfyUI-LatentSyncWrapper.git"
set "REPOS[42]=https://github.com/mingsky-ai/ComfyUI-MingNodes.git"
set "REPOS[43]=https://github.com/christian-byrne/audio-separation-nodes-comfyui.git"
set "REPOS[45]=https://github.com/niknah/ComfyUI-F5-TTS.git"
set "REPOS[46]=https://github.com/pythongosssss/ComfyUI-Custom-Scripts.git"

:: 克隆所有仓库到当前目录
for /L %%i in (0,1,42) do (
    echo 正在处理仓库: !REPOS[%%i]!
    set "URL=!REPOS[%%i]!"
    :: 提取仓库名
    for %%A in ("!URL!") do (
        set "DIRNAME=%%~nA"
        :: 替换特殊字符，避免路径问题
        set "DIRNAME=!DIRNAME:\=__!"
        set "DIRNAME=!DIRNAME:.git=!"
        :: 检查目标文件夹是否已存在
        if exist "!DIRNAME!" (
            echo 仓库 "!DIRNAME!" 已存在，跳过。
        ) else (
            echo 正在克隆到 "!DIRNAME!"
            git clone --depth=1 "!URL!" "!DIRNAME!"
            if %ERRORLEVEL% equ 0 (
                echo 仓库 !URL! 克隆成功
            ) else (
                echo 仓库 !URL! 克隆失败
            )
        )
    )
)
echo 所有仓库已处理完毕。
pause
