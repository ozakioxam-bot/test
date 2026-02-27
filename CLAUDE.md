# X投稿取得・自動配信ツール ― プロジェクト指示書

## プロジェクト概要

**目的:** 指定したXアカウントの特定期間・特定キーワードを含む投稿を取得し、メールフォーマットに変換してローカルで一括配信できるツールを開発する。

**主な成果物:**
- X投稿データを Markdown（MD）ファイルとしてダウンロードするツール
- 取得データをメールフォーマットに変換し、ローカルで擬似的に一括配信する仕組み

**スコープ外:** メール開封トラッキング・A/Bテスト・マーケティング分析ダッシュボード

---

## エージェントフレームワーク

このプロジェクトは `agent-orchestrator-starter-main/agents/_framework.md` のプロトコルに従う。

### 主要ドキュメント

| ファイル | 用途 |
|--------|------|
| `docs/requirements.md` | 要件定義（品質監査の基準） |
| `docs/specifications.md` | 仕様書（品質監査の基準） |
| `.agents/PROJECT.md` | エージェント間共有知識・Activity Log |
| `.agents/lessons.md` | 失敗・成功パターンの学習ログ |

### 推奨チェーン

| タスク | チェーン |
|--------|---------|
| バグ修正（簡単） | Scout → Builder → Radar |
| バグ修正（複雑） | Scout → Sherpa → Builder → Radar → Sentinel |
| 機能開発（小） | Builder → Radar |
| 機能開発（中） | Sherpa → Builder → Sentinel → Radar |
| セキュリティ監査 | Sentinel → Builder → Radar |
| PR準備 | Guardian → Judge |

---

## 品質保証ルール（完了条件）

> **実装完了 ≠ 「完了」。以下の全条件を満たして初めて「完了」と報告する。**

### 条件1: テスト2回パス

- テストは必ず **最低2回実行** し、**両方パス** することを確認する
- 1回目がパスしても2回目を省略してはならない（フレーキーテスト検出のため）
- `SKIP` はパスではなく「未完了」扱い（`_framework.md` Test Policy 準拠）

```
[1回目] pytest / npm test → PASS
[2回目] pytest / npm test → PASS  ← 両方パスで条件クリア
```

### 条件2: Sentinel（外部監査）パス

- 実装完了後、必ず **Sentinel エージェント** を呼び出してセキュリティ静的解析を実施する
- 監査の整合性確認ベースドキュメント:
  - `docs/requirements.md`（要件定義）
  - `docs/specifications.md`（仕様書）
- 監査で指摘された Critical / High は **必ず修正してから再監査** を受ける
- Sentinel の出力フォーマット（`_STEP_COMPLETE`）で `Status: SUCCESS` を確認する

```yaml
# Sentinel 呼び出し時の _AGENT_CONTEXT
_AGENT_CONTEXT:
  Role: Sentinel
  Task: セキュリティ静的解析 + docs/requirements.md / docs/specifications.md との整合性確認
  Mode: AUTORUN
```

### 完了の定義

```
テスト2回パス  AND  Sentinel外部監査パス  →  「完了」
      ↓                    ↓
  どちらか未達           →  「未完了」（修正・再検証が必要）
```

**どちらか一方でも未達の場合は「完了」と宣言してはならない。**

---

## セキュリティ要件（このプロジェクト固有）

X API・メール配信を扱うため、以下を厳守する:

- **APIキー・アクセストークン** は `.env` で管理。ハードコード・チャット貼り付け禁止（L4: 即時停止）
- **外部通信** は X API エンドポイントのみ。未承認の外部URLへのアクセス禁止
- **メールアドレスリスト（PII）** はローカルのみ保持。外部サービスへの送信禁止（Tier 2: 要確認）
- 取得投稿データにPIIが含まれる可能性があるため、出力・ログへの不用意な露出を防ぐ

---

## 重要な注意事項

- `_framework.md` の Double Confirmation Protocol (DCP) および Security Gates に従う
- 全成果物は `output/` フォルダに保存する
- セッション開始時は `.agents/PROJECT.md` と `.agents/lessons.md` を必ず読んでから作業を開始する
- コーディネーターはコードを書かない（計画 → 委任 → レビューが役割）
- 全出力は **日本語** で記述する
