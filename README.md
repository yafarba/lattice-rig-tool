# Universal Lattice Rig Tool

**Version:** 1.0 (2026)  
**License:** MIT (Free for educational, personal and commercial projects. If you use it, a credit is always appreciated.)  
**Gumroad:** [Download for Free on Gumroad](https://yafarba.gumroad.com/l/latticerigtool)

![Universal Lattice Rig Tool Demo](lattice_rig_tool_demo.gif)

---

## 🛠️ Requirements

*   **Autodesk Maya:** 2022 / 2023 / 2024 / 2025 / 2026+ (Python 3)

---

## 📝 Description

This script builds a complete lattice rig with aligned controls, clean hierarchy, and direct cluster connections. Customize controller shapes, colors, and sizes while removing repetitive setup and creating clean, production-ready rigs in seconds.

---

## ⚠️ Important Note

### Inherits Transform behavior (for `_latticeShape` and `_Base`):

*   **Enable (ON)** -> Use this when integrating the lattice into your rigging system. The lattice will follow the rig hierarchy and transform with it.
*   **Disable (OFF)** -> Use this when using the tool as a standalone deformer. The lattice stays in world space and will not inherit parent transforms (prevents drifting in scene space).

---

## 🚀 Installation and Launch Instructions

### Option 1: Run via Maya Scripts Folder (Recommended)

1. Copy the `lattice_rig_tool.py` file into your Maya scripts directory:
   * **Windows:** `Documents\maya\<version>\scripts\`
   * **macOS:** `/Users/<username>/Library/Preferences/Autodesk/maya/<version>/scripts/`
   * **Linux:** `~/maya/<version>/scripts/`

2. Open Maya, navigate to the **Script Editor**, and open a **PYTHON** tab.
3. Paste and execute the following code:

```python
import lattice_rig_tool
lattice_rig_tool.create_universal_lattice_rig_ui()
```

4. *(Optional)* Highlight this code in the Script Editor and middle-mouse drag it onto your **Shelf** to create a quick-access button.

### Option 2: Direct Execution without Copying Files

If you prefer not to move the file, open a **PYTHON** tab in the Script Editor, paste the code below, update the path, and run it:

```python
path = r"C:\Your_Folder_Path\lattice_rig_tool.py"
with open(path, "r", encoding="utf-8") as f:
    exec(f.read())
```

---

## 🛠️ How To Use

1. **Select** the geometry or group of objects in your scene.
2. **Launch** the tool, then set your divisions, control size, and color.
3. Click the **"Create Lattice Rig"** button.
4. Enjoy! 😊
