<div align="center">

# 🖥️ Paper Server Studio

### A modern GUI for managing Minecraft Paper servers.

![Version](https://img.shields.io/badge/Version-v1.0-blue)
![Python](https://img.shields.io/badge/Python-3.11+-yellow)
![Platform](https://img.shields.io/badge/Platform-Windows-blue)
![Minecraft](https://img.shields.io/badge/Minecraft-Paper-green)

⭐ If you enjoy this project, leave a star!

</div>

---

> [!WARNING]
> This project is currently in development. Bugs may exist and some features are still being improved.

> [!TIP]
> Always stop your server using the **Stop Server** button. This safely saves your world before shutting down.

---

# 📚 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Using Paper Server Studio](#-using-paper-server-studio)
- [Screenshots](#-screenshots)
- [FAQ](#-faq)
- [Troubleshooting](#-troubleshooting)
- [Roadmap](#-roadmap)
- [Changelog](#-changelog)
- [Contributing](#-contributing)
- [License](#-license)

---

# 📊 Development Progress

🟩🟩🟩🟩🟩🟩🟩🟩⬜⬜ **80% Complete**

Current Version

```
v1.0
```

---

# ✨ Features

- [x] Modern GUI
- [x] Start Server
- [x] Stop Server
- [x] Restart Server
- [x] Live Console
- [x] Send Commands
- [x] Edit server.properties
- [x] Open Server Folder
- [x] Safe World Saving
- [x] Server Status
- [x] RAM Selection
- [ ] Plugin Manager
- [ ] Automatic Backups
- [ ] World Manager
- [ ] Automatic Updates
- [ ] Multiple Servers
- [ ] Theme Support

---

# 📥 Installation

<details>

<summary><b>Click to expand</b></summary>

## 1.

Create a folder named

```
Paper 2026 Server
```

(Currently required.)

---

## 2.

Download a Paper server JAR.

Rename it

```
paper.jar
```

---

## 3.

Create

```
start.bat
```

Example

```bat
java -Xms2G -Xmx4G -jar paper.jar
pause
```

---

## 4.

Run

```
start.bat
```

Wait until the server says

```
Done!
```

Then type

```
stop
```

---

## 5.

Move

```
Paper Server Studio.exe
```

into the folder.

Example

```
Paper 2026 Server

├── Paper Server Studio.exe
├── paper.jar
├── start.bat
├── server.properties
├── plugins
├── world
├── world_nether
└── world_the_end
```

</details>

---

# 🚀 Using Paper Server Studio

### Start

Click

```
Start Server
```

---

### Stop

Click

```
Stop Server
```

The application safely sends

```
stop
```

to the server.

---

### Restart

Click

```
Restart
```

The server automatically saves before restarting.

---

### Console

Send commands like

```
say Hello!
```

```
weather clear
```

```
op Steve
```

Do **NOT** use

```
/
```

Example

✅

```
op Steve
```

❌

```
/op Steve
```

---

# ⚙️ Server Settings

Edit

- MOTD
- Max Players
- Difficulty
- Gamemode
- Online Mode
- View Distance
- PVP
- Spawn Animals
- Spawn Monsters
- Command Blocks
- Allow Flight

Restart the server after saving.

---

# 🖼️ Screenshots

*(Coming Soon)*

```
Dashboard
```

```
Console
```

```
Settings
```

```
Properties Editor
```

---

# ❓ FAQ

<details>

<summary><b>Does it support Spigot?</b></summary>

Yes.

</details>

<details>

<summary><b>Does it support Purpur?</b></summary>

Mostly.

</details>

<details>

<summary><b>Does it support multiple servers?</b></summary>

Not yet.

</details>

<details>

<summary><b>Does it work on Linux?</b></summary>

Not officially.

</details>

---

# 🔧 Troubleshooting

<details>

<summary><b>Java not found</b></summary>

Install Java and verify

```
java -version
```

works.

</details>

<details>

<summary><b>Missing paper.jar</b></summary>

Rename your server file

```
paper.jar
```

</details>

<details>

<summary><b>Cannot place blocks</b></summary>

Either OP yourself

```
op YourName
```

or set

```
spawn-protection=0
```

</details>

<details>

<summary><b>Cannot join server</b></summary>

Check

- Firewall
- IP
- Port
- Online Mode

</details>

---

# 🛣️ Roadmap

## Version 1.1

- [ ] Plugin Manager
- [ ] Automatic Updates
- [ ] Automatic Backups

## Version 1.2

- [ ] World Manager
- [ ] Player Manager
- [ ] Performance Graph

## Version 2.0

- [ ] Multi Server Support
- [ ] Server Wizard
- [ ] Theme Support
- [ ] Automatic Paper Downloads

---

# 📜 Changelog

<details>

<summary><b>Version History</b></summary>

## v1.0

- First public release
- Modern GUI
- Live Console
- Settings Editor
- Safe Shutdown
- Restart Button

</details>

---

# 🤝 Contributing

Bug reports, ideas, and pull requests are welcome.

---

# ⬇️ Download

Download the newest release from

```
Releases
```

on the right side of this GitHub repository.

---

# 📄 License

Choose your preferred license before publishing.

Recommended

- MIT
- Apache 2.0
- GPL v3

---

<div align="center">

## ❤️ Made by Kaz

Paper Server Studio is **not affiliated with Mojang Studios, Microsoft, or PaperMC.**

⭐ Thanks for checking out the project!

</div>
