#!/bin/bash
set -e

# List of custom node git repositories
REPOS=(
    "https://github.com/Comfy-Org/ComfyUI-Manager.git"
    "https://github.com/kijai/ComfyUI-WanVideoWrapper.git"
    "https://github.com/kijai/ComfyUI-KJNodes.git"
    "https://github.com/cubiq/ComfyUI_essentials.git"
    "https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git"
    "https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes.git"
    "https://github.com/rgthree/rgthree-comfy.git"
    "https://github.com/crystian/ComfyUI-Crystools.git"
    "https://github.com/cubiq/ComfyUI_FaceAnalysis.git"
    "https://github.com/cubiq/ComfyUI_InstantID.git"
    "https://github.com/cubiq/PuLID_ComfyUI.git"
    "https://github.com/Fannovel16/comfyui_controlnet_aux.git"
    "https://github.com/Fannovel16/ComfyUI-Frame-Interpolation.git"
    "https://github.com/FizzleDorf/ComfyUI_FizzNodes.git"
    "https://github.com/Gourieff/ComfyUI-ReActor.git"
    "https://github.com/huchenlei/ComfyUI-layerdiffuse.git"
    "https://github.com/jags111/efficiency-nodes-comfyui.git"
    "https://github.com/ltdrdata/ComfyUI-Impact-Pack.git"
    "https://github.com/ltdrdata/ComfyUI-Impact-Subpack.git"
    "https://github.com/ltdrdata/ComfyUI-Inspire-Pack.git"
    "https://github.com/melMass/comfy_mtb.git"
    "https://github.com/storyicon/comfyui_segment_anything.git"
    "https://github.com/WASasquatch/was-node-suite-comfyui.git"
    "https://github.com/chflame163/ComfyUI_LayerStyle.git"
    "https://github.com/chflame163/ComfyUI_LayerStyle_Advance.git"
    "https://github.com/shadowcz007/comfyui-mixlab-nodes.git"
    "https://github.com/yolain/ComfyUI-Easy-Use.git"
    "https://github.com/kijai/ComfyUI-IC-Light.git"
    "https://github.com/siliconflow/BizyAir.git"
    "https://github.com/lquesada/ComfyUI-Inpaint-CropAndStitch.git"
    "https://github.com/lldacing/comfyui-easyapi-nodes.git"
    "https://github.com/kijai/ComfyUI-FluxTrainer.git"
    "https://github.com/kijai/ComfyUI-SUPIR.git"
    "https://github.com/MrForExample/ComfyUI-3D-Pack.git"
    "https://github.com/alt-key-project/comfyui-dream-video-batches.git"
    "https://github.com/nunchaku-tech/ComfyUI-nunchaku.git"
    "https://github.com/Dontdrunk/ComfyUI-DD-Translation.git"
    "https://github.com/AlekPet/ComfyUI_Custom_Nodes_AlekPet.git"
    "https://github.com/TTPlanetPig/Comfyui_TTP_Toolset.git"
    "https://github.com/ZenAI-Vietnam/ComfyUI-Kontext-Inpainting.git"
    "https://github.com/EvilBT/ComfyUI_SLK_joy_caption_two.git"
    "https://github.com/ShmuelRonen/ComfyUI-LatentSyncWrapper.git"
    "https://github.com/mingsky-ai/ComfyUI-MingNodes.git"
)

TARGET_DIR="/app/custom_nodes"
MAX_RETRIES=3
RETRY_DELAY=5 # in seconds

# Ensure the target directory exists
mkdir -p "$TARGET_DIR"
cd "$TARGET_DIR"

for repo in "${REPOS[@]}"; do
    repo_name=$(basename "$repo" .git)
    echo "Cloning $repo_name..."
    
    retries=0
    until git clone --depth=1 "$repo"; do
        retries=$((retries+1))
        if [ $retries -ge $MAX_RETRIES ]; then
            echo "Failed to clone $repo after $MAX_RETRIES attempts." >&2
            exit 1
        fi
        echo "Clone failed for $repo. Retrying in $RETRY_DELAY seconds... (Attempt $((retries+1))/$MAX_RETRIES)"
        sleep $RETRY_DELAY
    done
done

echo "All custom nodes cloned successfully." 