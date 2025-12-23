# 智能個人財務管理系統 (Smart Finance Manager)

這是一個基於 **Python** 開發的桌面端個人財務管理應用程式。旨在幫助使用者追蹤日常收支、設定財務目標，並透過視覺化圖表與自動化建議優化個人的理財習慣。

---

## 核心功能

* **使用者驗證系統**：支援多使用者註冊與登入，確保個人財務資料的隱私與安全性。
* **收支紀錄管理**：提供直覺的介面輸入收支資料，包含類別篩選（如：餐飲、薪資、交通等）。
* **歷史明細查詢**：以表格形式（Treeview）完整呈現所有交易紀錄，方便隨時追蹤。
* **視覺化圖表分析**：整合 `Matplotlib` 自動生成支出結構圓餅圖，掌握金流去向。
* **財務建議與預算追蹤**：使用者可設定每月預算上限，系統將自動分析當前消費狀態並給予健康警示。
* **本地資料庫存取**：使用 `SQLite` 進行資料持久化儲存，程式關閉後資料不遺失。

---

## 系統架構

本專案採用 **MVC (Model-View-Controller)** 的設計思想開發：

* **Model (資料層)**：`DBManager` 類別，負責所有 SQLite 資料庫的 CRUD 操作。
* **View / Controller (介面與邏輯層)**：`FinanceApp` 類別，負責 Tkinter GUI 渲染與邏輯處理。



[Image of Model-View-Controller architecture diagram]


---

## 技術棧 (Tech Stack)

* **程式語言**：Python 3.x
* **圖形介面**：Tkinter (Python Standard Library)
* **資料庫**：SQLite 3
* **數據繪圖**：Matplotlib

---

## 安裝與執行說明

### 1. 安裝必要套件
本系統需要額外安裝 `matplotlib` 庫來支援圖表功能。請在終端機執行：

```bash
pip install matplotlib
