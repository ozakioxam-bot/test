# Agent Orchestrator Starter - 要件定義書

| 項目 | 内容 |
|------|------|
| ドキュメントID | AOS-SPEC-001 |
| バージョン | 1.0.0 |
| 作成日 | 2026-02-27 |
| ステータス | Draft |

---

## 目次

1. [プロジェクト概要](#1-プロジェクト概要)
2. [システム構成](#2-システム構成)
3. [アーキテクチャ仕様](#3-アーキテクチャ仕様)
4. [Double Confirmation Protocol (DCP) 仕様](#4-double-confirmation-protocol-dcp-仕様)
5. [ガードレール仕様](#5-ガードレール仕様)
6. [パーミッション設定仕様](#6-パーミッション設定仕様)
7. [MCP設定仕様](#7-mcp設定仕様)
8. [エージェント仕様](#8-エージェント仕様)
9. [Chain Templates 仕様](#9-chain-templates-仕様)
10. [Complexity Assessment 仕様](#10-complexity-assessment-仕様)
11. [Security by Default 仕様](#11-security-by-default-仕様)
12. [運用仕様](#12-運用仕様)

---

## 1. プロジェクト概要

| 項目 | 内容 |
|------|------|
| 名称 | Agent Orchestrator Starter |
| 目的 | 初心者向け68エージェントオーケストレーションフレームワーク |
| 対象環境 | Claude Code Agent Teams API |
| 設計思想 | Hub-spokeモデルによる安全なマルチエージェント協調 |

### 1.1 設計原則

| SPC-001 | 原則 | 説明 |
|---------|------|------|
| SPC-001-01 | Hub-spoke | 全通信はオーケストレーター（Nexus/Rally）経由。直接Agent-to-Agent通信は禁止 |
| SPC-001-02 | Minimum viable chain | 必要最小限のエージェントで構成 |
| SPC-001-03 | File ownership is law | 並列実行時、各ファイルのオーナーは1つだけ |
| SPC-001-04 | Fail fast, recover smart | ガードレール L1-L4 で早期検出、可能なら自動回復 |
| SPC-001-05 | Context is precious | `.agents/PROJECT.md` + `.agents/LUNA_CONTEXT.md` でエージェント間の知識を共有 |
| SPC-001-06 | CEO-first for business | ビジネス判断は技術実装の前にCEOが方針を出す |
| SPC-001-07 | Simplicity first | 最小影響コードを強制。過剰設計より3行の重複を許容 |
| SPC-001-08 | Root cause only | 一時的修正禁止。根本原因を見つけて直す |
| SPC-001-09 | Trust but Verify | AI生成コードを信頼するが、必ず検証する |
| SPC-001-10 | Secrets never in code | シークレットは環境変数 or Vault経由のみ。ハードコード禁止（L4） |
| SPC-001-11 | Read-only by default | 自プロジェクト以外のリポジトリは読み取り専用 |
| SPC-001-12 | Double confirm for danger | 危険な操作は二重確認を強制（DCP） |

---

## 2. システム構成

### SPC-100: ディレクトリ構成

```
agent-orchestrator-starter/
├── agents/
│   ├── _framework.md          # 全エージェント共通プロトコル
│   ├── <agent-name>.md        # 68個の専門エージェント定義
│   └── <agent-name>/
│       └── references/        # 各エージェントの参考資料
├── templates/
│   ├── settings.json          # 3層パーミッション設定テンプレート
│   └── mcp-settings.json      # MCP安全設定テンプレート
└── docs/
    └── specification.md       # 本ドキュメント
```

### SPC-101: 構成要素

| ID | 要素 | ファイル数 | 説明 |
|----|------|-----------|------|
| SPC-101-01 | Framework Protocol | 1 | `agents/_framework.md` - 全エージェント共通プロトコル |
| SPC-101-02 | Agent Definitions | 68 | `agents/*.md` - 専門エージェント定義ファイル |
| SPC-101-03 | Reference Materials | 267 | `agents/*/references/` - 各エージェントの参考資料 |
| SPC-101-04 | Permission Template | 1 | `templates/settings.json` - 3層パーミッション設定 |
| SPC-101-05 | MCP Template | 1 | `templates/mcp-settings.json` - MCP安全設定 |

### SPC-102: 配置先

ユーザーのプロジェクトにおいて、以下のパスに配置する。

| 要素 | 配置先パス |
|------|-----------|
| Framework Protocol | `.claude/agents/_framework.md` |
| Agent Definitions | `.claude/agents/<agent-name>.md` |
| Reference Materials | `.claude/agents/<agent-name>/references/` |
| Permission Template | `.claude/settings.json` |
| MCP Template | `.claude/mcp-settings.json` |

---

## 3. アーキテクチャ仕様

### SPC-200: 実行アーキテクチャ

```
User Request
     |
     v
  [Nexus] ---- Phase 0: EXECUTIVE_REVIEW
     |
     +---> CEO判断が必要？ → [CEO] → 方針・制約を付与
     |
     +---> Sequential: Agent1 → Agent2 → Agent3（ロールシミュレーション）
     |
     +---> Parallel: Rally → TeamCreate → Teammates（実セッション並列）
```

### SPC-201: 実行モード

| ID | モード | トリガー | 動作 |
|----|--------|---------|------|
| SPC-201-01 | AUTORUN_FULL | Default | 全自動実行（ガードレールのみ） |
| SPC-201-02 | AUTORUN | `## NEXUS_AUTORUN` | SIMPLE自動、COMPLEX→Guided |
| SPC-201-03 | GUIDED | `## NEXUS_GUIDED` | 判断ポイントで確認 |
| SPC-201-04 | INTERACTIVE | `## NEXUS_INTERACTIVE` | 各ステップで確認 |

### SPC-202: Sequential実行（ロールシミュレーション）

Nexusが単一セッション内で各エージェントの役割を順次シミュレートする方式。

- Agent1 → Agent2 → Agent3 の順に実行
- 各ステップの出力が次のステップの入力になる
- AUTORUN_FULLモードでは確認なしで自動進行

### SPC-203: Parallel実行（マルチセッション並列）

Rally が Claude Code Agent Teams API を使用して複数セッションを同時実行する方式。

| ID | 制約 | 値 |
|----|------|-----|
| SPC-203-01 | 最大ブランチ数 | 4 |
| SPC-203-02 | ブランチあたり最大ステップ | 5 |
| SPC-203-03 | 合計並列ステップ | 15 |

### SPC-204: File Ownership（並列実行時）

```yaml
ownership_map:
  teammate_a:
    exclusive_write: [src/features/auth/**]
    shared_read: [src/types/**]
  teammate_b:
    exclusive_write: [src/features/profile/**]
    shared_read: [src/types/**]
```

| ID | ルール | 説明 |
|----|--------|------|
| SPC-204-01 | exclusive_write | そのチームメイトのみ書き込み可 |
| SPC-204-02 | shared_read | 読み取り専用（全員） |
| SPC-204-03 | 重複禁止 | オーナーシップの重複は許可しない |

### SPC-205: Plan Mode Enforcement

Complexity Assessment と連動し、計画モードの使用を制御する。

| 判定 | Plan Mode | 動作 |
|------|-----------|------|
| COMPLEX（3ステップ以上 or 4ファイル以上） | 必須 | `.agents/todo.md` に計画記録後に実装開始 |
| SIMPLE | 任意 | ただし失敗時は即座にPlanモードに切替 |

### SPC-206: AUTORUN入出力フォーマット

**入力フォーマット:**

```yaml
_AGENT_CONTEXT:
  Role: AgentName
  Task: [タスク内容]
  Mode: AUTORUN
```

**出力フォーマット:**

```yaml
_STEP_COMPLETE:
  Agent: AgentName
  Status: SUCCESS | PARTIAL | BLOCKED
  Output: [結果]
  Next: [NextAgent] | VERIFY | DONE
```

### SPC-207: Nexus Hub Mode Handoff

```text
## NEXUS_HANDOFF
- Step: [X/Y]
- Agent: AgentName
- Summary: [1-3行]
- Key findings: [list]
- Artifacts: [files/commands]
- Risks: [list]
- Suggested next agent: [Agent] (reason)
- Next action: CONTINUE | VERIFY | DONE
```

---

## 4. Double Confirmation Protocol (DCP) 仕様

### SPC-300: 概要

ユーザーが「はい」「OK」「進めて」と承認しても、危険な操作は二重確認を強制する。
初心者がリスクを理解せずに承認してしまう事故を防ぐ仕組み。

**全エージェントがこのプロトコルに従う。例外はない。**

### SPC-301: Tier 1 - 絶対禁止（Override不可）

何回確認しても絶対に実行しない。ユーザーが明示的に要求しても拒否する。

| ID | 操作 | なぜ危険か |
|----|------|-----------|
| SPC-301-01 | チャットへの秘密情報の貼り付け・要求 | 会話履歴はAnthropicサーバーに送信される。一度送信すると取消不可。APIキー漏洩で不正利用・課金被害が発生する |
| SPC-301-02 | Read-onlyリポジトリへの push / commit / 編集 | 本番サービスに影響を与える可能性。復旧に数時間〜数日。最悪の場合ユーザーデータが破損する |
| SPC-301-03 | `.env` / `.secrets/` / `credentials/` への書込 | 既存の認証情報を上書きするとサービスが即座に停止。手動復旧が必要 |
| SPC-301-04 | 秘密情報のハードコード | ソースコードに埋め込まれた秘密情報はGit履歴に永久に残る。`git push`で全世界に公開される可能性 |

**応答フォーマット:**

```
BLOCKED: この操作は安全上の理由で実行できません。

操作: [ユーザーが要求した内容]
リスク: [上記テーブルの「なぜ危険か」]
代替手段: [安全な方法の提案]

この制限はフレームワークの絶対ルールであり、解除できません。
どうしても必要な場合は、エンジニアに相談の上、人間の手で直接実行してください。
```

**代替案ガイド:**

| 操作 | 代替手段 |
|------|---------|
| 秘密情報のチャット貼り付け | `.env.example` を作成 → 手動で値を入力 |
| Read-onlyリポジトリへの書込 | 自プロジェクト内で変更 → 元リポジトリにはPRで反映 |
| `.env` / `.secrets` への書込 | `.env.example` を編集 → 手動で `.env` にコピー |
| 秘密情報のハードコード | 環境変数に設定 → `os.environ` で読み込み |

### SPC-302: Tier 2 - セキュリティリスク操作（エンジニア確認推奨）

秘密情報・個人情報の流出、本番ユーザーへの影響があり得る操作。
理由付き承認に加え、エンジニアへの相談を推奨する。

| ID | カテゴリ | 対象操作 | リスク | エンジニア相談理由 |
|----|---------|---------|-------|------------------|
| SPC-302-01 | 本番環境操作 | productionへのデプロイ・設定変更 | 実際のユーザーに直接影響 | リリース責任者が適任 |
| SPC-302-02 | 本番DB操作 | `DROP TABLE`, `DELETE`(WHERE句なし), `TRUNCATE` | ユーザーデータ完全消失 | DB管理者がバックアップ状況を把握 |
| SPC-302-03 | PII処理 | PIIを含むデータの取得・加工・出力 | 個人情報保護法違反 | 法務が法的リスクを判断 |
| SPC-302-04 | 認証・認可変更 | ログイン処理、権限制御、IAMポリシー | セキュリティホール | セキュリティ担当にレビュー依頼 |
| SPC-302-05 | 外部データ送信 | 外部APIへのPOST、Webhook送信 | 意図しないデータ流出・SSRF | エンジニアに送信データ確認 |
| SPC-302-06 | CI/CD本番パイプライン変更 | 本番デプロイに関わるActions・スクリプト | ミスが自動で本番に反映 | インフラ担当にレビュー依頼 |

**確認フォーマット:**

```
------------------------------------------------------------
SAFETY CHECK: セキュリティリスクがある操作です

操作: [具体的に何をするか]
リスク: [秘密情報/個人情報/本番ユーザーへの影響]
影響範囲: [影響を受けるユーザー・データ・サービス]
相談推奨: [この操作について相談すべきエンジニア・担当者]

エンジニアに確認済みですか？
→ 確認済みの場合: 「○○さんに確認済み」等を添えて承認
→ 未確認の場合: 先にエンジニアに相談することを推奨します
------------------------------------------------------------
```

### SPC-303: Tier 3 - 破壊的操作（リスク説明のみ）

セキュリティリスクはないが、データ消失の可能性がある操作。
自分のリポジトリ・ローカル環境内の操作であれば、リスクを理解した上でエンジニア確認なしで実行可能。

| ID | カテゴリ | 対象操作 | リスク説明 |
|----|---------|---------|-----------|
| SPC-303-01 | 破壊的Git操作 | `git reset --hard`, `git push --force`, `git clean -f`, `git branch -D` | コミット履歴・未コミットの変更が消失。`git stash` でバックアップ推奨 |
| SPC-303-02 | ファイル大量削除 | `rm -rf`、ディレクトリ全体の削除 | Git未管理ファイルは永久に失われる |
| SPC-303-03 | ローカルDB操作 | 開発用DBでの `DROP`, `TRUNCATE` | ローカルデータ消失。事前ダンプ推奨 |
| SPC-303-04 | 依存パッケージ追加 | `npm install`, `pip install`（新規） | `npm audit` / `pip audit` を先に実行 |
| SPC-303-05 | 権限変更 | `chmod`, `chown`（ローカル） | `chmod 777` は避け、最小限の権限に |

**確認フォーマット:**

```
注意: [操作内容] は [リスク説明]
→ 実行しますか？（「はい」で実行します）
```

理由なしの「はい」で実行可能。ただし初回はリスクを説明する。

### SPC-304: Tier 4 - 通常操作（確認なし）

セキュリティリスクも破壊リスクもない操作は、確認なしで実行する。

- ファイルの作成・編集（機密ファイル以外）
- `git add` / `git commit`（自分のリポジトリ）
- テスト実行、linter / formatter 実行
- コード閲覧・検索

### SPC-305: DCP 運用ルール

| ID | ルール | 説明 |
|----|--------|------|
| SPC-305-01 | Tier 2 エンジニア確認推奨 | 「確認済み」の自己申告で実行可。嘘をつくリスクはユーザー責任 |
| SPC-305-02 | Tier 3 理由なし承認で実行可 | リスク説明は行うが、判断はユーザーに委ねる |
| SPC-305-03 | 代替案必須提示 | 危険な操作を確認する際は、より安全な方法を併せて提案 |
| SPC-305-04 | 操作ログ記録 | Tier 2 経由で実行された操作は `.agents/lessons.md` に記録 |
| SPC-305-05 | セキュリティ側に倒す | Tier 2 か Tier 3 か判断できない場合は Tier 2 として扱う |

### SPC-306: エンジニア確認不要判定基準

以下の**全て**に該当する場合、エンジニア確認なしで進めてよい。

| チェック項目 |
|------------|
| 自分のリポジトリ内の操作である |
| 秘密情報（APIキー・パスワード等）に触れない |
| 個人情報（PII）を扱わない |
| 本番環境・本番ユーザーに影響しない |
| 他のチームメンバーの作業に影響しない |

1つでも該当しない場合は、エンジニアに相談してから進める。

### SPC-307: DCP フローチャート

```
ユーザーの操作要求
    |
    v
Tier 1（絶対禁止）に該当？
    |
   YES → BLOCKED 応答 + 代替案提示 → 終了
    |
   NO
    v
セキュリティリスクあり？（秘密情報/PII/本番影響）
    |
   YES → Tier 2: リスク説明 + エンジニア確認推奨
    |      → 「確認済み」or 理由付き承認 → 実行
    |
   NO
    v
破壊的操作？（データ消失の可能性）
    |
   YES → Tier 3: リスク説明 → 「はい」で実行可
    |
   NO
    v
Tier 4（通常操作）→ そのまま実行
```

---

## 5. ガードレール仕様

### SPC-400: ガードレールレベル

| ID | Level | Trigger | Action |
|----|-------|---------|--------|
| SPC-400-01 | L1 | lint_warning | ログのみ、続行 |
| SPC-400-02 | L2 | test_failure <20% | 自動修正試行（最大3回） |
| SPC-400-03 | L3 | test_failure >50% | ロールバック + 再分解 |
| SPC-400-04 | L4 | critical_security | 即時停止 |

### SPC-401: Security Gates（L4連動）

以下はすべて L4（即時停止）扱い。DCP Tier 1 に該当し、ユーザーが承認しても絶対に実行しない。

| ID | ゲート | 検出対象 |
|----|--------|---------|
| SPC-401-01 | シークレットハードコード | APIキー・パスワード等のソースコード内埋込 |
| SPC-401-02 | Read-only書込 | Read-onlyリポジトリへの push / commit / 編集 |
| SPC-401-03 | 未承認外部通信 | `curl` / `wget` による未承認の外部通信 |
| SPC-401-04 | 機密ファイル書込 | `.env` / `.secrets/` / `credentials/` への書込 |
| SPC-401-05 | audit未実行 | 依存パッケージ追加時に `npm audit` / `pip audit` 未実行 |

### SPC-402: エスカレーションフロー

```
L1 → 改善なし → L2 → 自動回復成功 → CONTINUE
                    → 回復失敗 → L3 → 解決 → CONTINUE
                                    → 重大 → L4 → ROLLBACK + STOP
```

---

## 6. パーミッション設定仕様

### SPC-500: settings.json テンプレート

配置先: `.claude/settings.json`

### SPC-501: allow（確認なしで実行許可）

| ID | パーミッション | 説明 |
|----|--------------|------|
| SPC-501-01 | `Read` | ファイル読み取り |
| SPC-501-02 | `Glob` | ファイルパターン検索 |
| SPC-501-03 | `Grep` | ファイル内容検索 |
| SPC-501-04 | `Bash(git status)` | Git状態確認 |
| SPC-501-05 | `Bash(git diff:*)` | Git差分確認 |
| SPC-501-06 | `Bash(git log:*)` | Gitログ確認 |
| SPC-501-07 | `Bash(git branch:*)` | Gitブランチ確認 |
| SPC-501-08 | `Bash(npm test:*)` | npmテスト実行 |
| SPC-501-09 | `Bash(npm run lint:*)` | npmlint実行 |
| SPC-501-10 | `Bash(pytest:*)` | pytestテスト実行 |
| SPC-501-11 | `Bash(python -m pytest:*)` | pytest実行（モジュール形式） |

### SPC-502: ask（ユーザー確認後に実行）

| ID | パーミッション | 説明 |
|----|--------------|------|
| SPC-502-01 | `Write` | ファイル書き込み |
| SPC-502-02 | `Edit` | ファイル編集 |
| SPC-502-03 | `Bash(git add:*)` | Gitステージング |
| SPC-502-04 | `Bash(git commit:*)` | Gitコミット |
| SPC-502-05 | `Bash(npm install:*)` | npmパッケージインストール |
| SPC-502-06 | `Bash(pip install:*)` | pipパッケージインストール |
| SPC-502-07 | `Bash(docker:*)` | Docker操作 |

### SPC-503: deny（実行禁止）

| ID | パーミッション | 理由 |
|----|--------------|------|
| SPC-503-01 | `Bash(curl:*)` | 未承認外部通信防止 |
| SPC-503-02 | `Bash(wget:*)` | 未承認外部通信防止 |
| SPC-503-03 | `Bash(rm -rf:*)` | 大量ファイル削除防止 |
| SPC-503-04 | `Bash(git push:*)` / `Bash(git push)` | 意図しないpush防止 |
| SPC-503-05 | `Bash(git remote set-url:*)` | リモートURL改竄防止 |
| SPC-503-06 | `Bash(git reset --hard:*)` | 履歴消失防止 |
| SPC-503-07 | `Bash(git push --force:*)` | 強制push防止 |
| SPC-503-08 | `Bash(git clean -f:*)` | 未追跡ファイル消失防止 |
| SPC-503-09 | `Read/Write/Edit(.env)` | 機密ファイルアクセス防止 |
| SPC-503-10 | `Read/Write/Edit(.env.*)` | 機密ファイルアクセス防止 |
| SPC-503-11 | `Read/Write/Edit(.secrets/**)` | 機密ファイルアクセス防止 |
| SPC-503-12 | `Read/Write/Edit(credentials/**)` | 機密ファイルアクセス防止 |
| SPC-503-13 | `WebFetch` | 外部URL取得防止 |

---

## 7. MCP設定仕様

### SPC-600: mcp-settings.json テンプレート

配置先: `.claude/mcp-settings.json`

| ID | 設定項目 | 値 | 説明 |
|----|---------|-----|------|
| SPC-600-01 | `enableAllProjectMcpServers` | `false`（必須） | プロジェクトMCPサーバーの自動有効化を禁止 |
| SPC-600-02 | `enabledMcpJsonServers` | `["github", "memory"]` | 許可するMCPサーバー |
| SPC-600-03 | `disabledMcpJsonServers` | `["filesystem"]` | 明示的に無効化するMCPサーバー |

### SPC-601: MCP安全方針

- `enableAllProjectMcpServers` を `true` にすることは禁止
- 新しいMCPサーバーの追加時はセキュリティレビュー必須（DCP Tier 2 相当）
- `filesystem` MCPサーバーはRead/Write/Edit/Glob/Grepツールで代替可能なため無効化

---

## 8. エージェント仕様

### SPC-700: エージェント一覧

68個の専門エージェントをカテゴリ別に分類する。

#### SPC-701: オーケストレーション（4エージェント）

| エージェント名 | 役割 | コード実装 |
|--------------|------|-----------|
| Nexus | 専門AIエージェントチームを統括するオーケストレーター。要求分解、チェーン設計、AUTORUNモード自動進行 | 不可 |
| Rally | Claude Code Agent Teams APIを使用したマルチセッション並列オーケストレーター | 不可 |
| Sherpa | タスク分解ガイド。複雑なタスクを15分以内で完了できるAtomic Stepに分解 | 不可 |
| CEO | ビジネス意思決定。思想を守りながら市場を創造する判断を出す | 不可 |

#### SPC-702: 実装（4エージェント）

| エージェント名 | 役割 | コード実装 |
|--------------|------|-----------|
| Builder | 本番実装の職人。型安全・TDD・DDD・パフォーマンス最適化 | 可 |
| Artisan | フロントエンド本番実装。React/Vue/Svelte、Hooks設計、状態管理、Server Components | 可 |
| Forge | プロトタイプ作成。完璧より動くものを優先 | 可 |
| Scaffold | クラウドインフラ（Terraform等）とローカル開発環境の環境プロビジョニング | 可 |

#### SPC-703: 品質（5エージェント）

| エージェント名 | 役割 | コード実装 |
|--------------|------|-----------|
| Radar | テスト追加・フレーキーテスト修正・カバレッジ向上 | 可 |
| Judge | コードレビュー・バグ検出・品質評価 | 不可 |
| Auditor | スペック準拠監査。設計・実装がREADME仕様から逸脱していないかを検証 | 不可 |
| Warden | V.A.I.R.E.品質基準の守護者。リリース前評価、スコアカード査定、合否判定 | 不可 |
| Hone | PDCAサイクルで品質を反復的に向上させるQuality Orchestrator | 不可 |

#### SPC-704: セキュリティ（3エージェント）

| エージェント名 | 役割 | コード実装 |
|--------------|------|-----------|
| Sentinel | セキュリティ静的分析（SAST）。脆弱性パターン検出・入力検証追加 | 可 |
| Probe | OWASP ZAP/Burp Suite連携、ペネトレーションテスト計画、DAST実行 | 可 |
| Specter | 並行性・非同期処理の「見えない」問題を検出。Race Condition、Memory Leak、Deadlock | 不可 |

#### SPC-705: 分析・調査（4エージェント）

| エージェント名 | 役割 | コード実装 |
|--------------|------|-----------|
| Analyst | データ分析。Redash API等でデータ取得、指標定義・前提条件を明示した上で示唆 | 不可 |
| Scout | バグ調査・根本原因分析（RCA）。再現手順と修正箇所を特定 | 不可 |
| Lens | コードベース理解・調査。機能探索・データフロー追跡 | 不可 |
| Rewind | Git履歴調査、リグレッション根本原因分析、コード考古学 | 不可 |

#### SPC-706: 設計（6エージェント）

| エージェント名 | 役割 | コード実装 |
|--------------|------|-----------|
| Architect | 新しいエージェントを設計・生成するメタデザイナー | 不可 |
| Schema | DBスキーマ設計・マイグレーション作成・ER図設計 | 可 |
| Cipher | ユーザーの曖昧な要求を正確な仕様に変換 | 不可 |
| Bridge | ビジネス要件と技術実装の翻訳・調停 | 不可 |
| Gateway | API設計・レビュー、OpenAPI仕様生成、バージョニング戦略 | 可 |
| Atlas | 依存関係・循環参照・God Class分析、ADR/RFC作成 | 不可 |

#### SPC-707: テスト（3エージェント）

| エージェント名 | 役割 | コード実装 |
|--------------|------|-----------|
| Voyager | E2Eテスト専門。Playwright/Cypress設定、Page Object設計 | 可 |
| Showcase | Storybookストーリー作成・カタログ管理・Visual Regression連携 | 可 |
| Director | Playwright E2Eテストを活用した機能デモ動画の自動撮影 | 可 |

#### SPC-708: UI/UX（5エージェント）

| エージェント名 | 役割 | コード実装 |
|--------------|------|-----------|
| Vision | UI/UXクリエイティブディレクション、Design System構築 | 不可 |
| Muse | デザイントークン定義・管理、Design System構築 | 可 |
| Palette | ユーザビリティ改善、インタラクション品質向上、a11y対応 | 可 |
| Flow | CSS/JSアニメーション実装。ホバー効果、ローディング状態、モーダル遷移 | 可 |
| Echo | ペルソナになりきりUIフローを検証し、混乱ポイントを報告 | 不可 |

#### SPC-709: ドキュメント（4エージェント）

| エージェント名 | 役割 | コード実装 |
|--------------|------|-----------|
| Scribe | 仕様書・設計書・実装チェックリスト・テスト仕様書作成 | 不可 |
| Quill | JSDoc/TSDoc追加、README更新、any型の型定義化 | 可 |
| Morph | ドキュメントフォーマット変換（Markdown↔Word/Excel/PDF/HTML） | 可 |
| Canvas | コード・設計・コンテキストをMermaid図、ASCIIアート、draw.ioに変換 | 可 |

#### SPC-710: 運用（5エージェント）

| エージェント名 | 役割 | コード実装 |
|--------------|------|-----------|
| Gear | 依存関係管理、CI/CD最適化、Docker設定、運用オブザーバビリティ | 可 |
| Triage | 障害発生時の初動対応、影響範囲特定、復旧手順策定 | 不可 |
| Launch | リリース計画・実行・追跡、バージョニング戦略、CHANGELOG生成 | 可 |
| Guardian | Git/PRの番人。Signal/Noise分析、コミット粒度最適化 | 不可 |
| Harvest | GitHub PR情報収集・レポート生成・作業報告書作成 | 不可 |

#### SPC-711: 戦略（5エージェント）

| エージェント名 | 役割 | コード実装 |
|--------------|------|-----------|
| Compete | 競合調査、差別化ポイント特定、SWOT分析 | 不可 |
| Spark | 既存データ/ロジックを活用した新機能提案 | 不可 |
| Experiment | A/Bテスト設計、仮説ドキュメント作成、統計的有意性判定 | 可 |
| Voice | ユーザーフィードバック収集、NPS調査設計、感情分析 | 不可 |
| Researcher | ユーザーリサーチ。インタビュー設計、ユーザビリティテスト計画 | 不可 |

#### SPC-712: データ（2エージェント）

| エージェント名 | 役割 | コード実装 |
|--------------|------|-----------|
| Stream | ETL/ELTパイプライン設計、Kafka/Airflow/dbt設計 | 可 |
| Tuner | EXPLAIN ANALYZE分析、クエリ最適化、インデックス推奨 | 可 |

#### SPC-713: パフォーマンス・リファクタリング（3エージェント）

| エージェント名 | 役割 | コード実装 |
|--------------|------|-----------|
| Bolt | フロントエンド/バックエンド両面のパフォーマンス改善 | 可 |
| Zen | リファクタリング・コード品質改善。動作を変えずに可読性・保守性を向上 | 可 |
| Sweep | 不要ファイル検出・未使用コード特定・安全な削除提案 | 不可 |

#### SPC-714: グロース・マーケティング（3エージェント）

| エージェント名 | 役割 | コード実装 |
|--------------|------|-----------|
| Growth | SEO/SMO/CROの3軸で成長を支援 | 可 |
| Retain | リテンション施策、チャーン予防、ゲーミフィケーション | 不可 |
| Pulse | KPI定義、トラッキングイベント設計、ダッシュボード仕様作成 | 不可 |

#### SPC-715: 国際化・標準化（3エージェント）

| エージェント名 | 役割 | コード実装 |
|--------------|------|-----------|
| Polyglot | 国際化（i18n）・ローカライズ（l10n）。翻訳キー管理、RTL対応 | 可 |
| Canon | 世界標準・業界標準準拠評価。OWASP/WCAG/OpenAPI/ISO 25010等 | 不可 |
| Horizon | 非推奨ライブラリ検出、新技術PoC作成、レガシー更新 | 可 |

#### SPC-716: コンテンツ・デモ（2エージェント）

| エージェント名 | 役割 | コード実装 |
|--------------|------|-----------|
| Bard | Developer grumble agent。Git履歴・PRをモノローグに変換 | 可 |
| Reel | ターミナル録画・CLIデモ動画生成。VHS/terminalizer/asciinema | 可 |

#### SPC-717: 開発ツール・CLI（2エージェント）

| エージェント名 | 役割 | コード実装 |
|--------------|------|-----------|
| Anvil | Terminal UI構築、CLI開発支援、開発ツール統合 | 可 |
| Arena | codex exec / gemini CLI を使った競争開発・協力開発 | 可 |

#### SPC-718: 構造・影響分析（3エージェント）

| エージェント名 | 役割 | コード実装 |
|--------------|------|-----------|
| Grove | リポジトリ構造の設計・最適化・監査 | 不可 |
| Ripple | 変更前の影響分析。依存関係・パターン一貫性の両面から評価 | 不可 |
| Trace | セッションリプレイ分析、ペルソナベース行動パターン抽出 | 不可 |

#### SPC-719: 意思決定・ナビゲーション（2エージェント）

| エージェント名 | 役割 | コード実装 |
|--------------|------|-----------|
| Magi | 3視点（論理・共感・実利）による多角的意思決定 | 不可 |
| Navigator | Playwright/Chrome DevToolsを活用したブラウザ操作自動化 | 可 |

---

## 9. Chain Templates 仕様

### SPC-800: 推奨チェーンテンプレート

| ID | タスク | チェーン | 説明 |
|----|--------|---------|------|
| SPC-800-01 | バグ修正（簡単） | Scout → Builder → Radar | 調査 → 修正 → テスト |
| SPC-800-02 | バグ修正（複雑） | Scout → Sherpa → Builder → Radar → Sentinel | 調査 → 分解 → 修正 → テスト → セキュリティ確認 |
| SPC-800-03 | 機能開発（小） | Builder → Radar | 実装 → テスト |
| SPC-800-04 | 機能開発（中） | Sherpa → Forge → Builder → Radar | 分解 → プロトタイプ → 実装 → テスト |
| SPC-800-05 | 機能開発（大） | Sherpa → Rally(Builder + Artisan + Radar) | 分解 → 並列実装 |
| SPC-800-06 | リファクタリング | Zen → Radar | リファクタ → テスト |
| SPC-800-07 | セキュリティ監査 | Sentinel → Builder → Radar | SAST → 修正 → テスト |
| SPC-800-08 | 機能開発（セキュリティ重要） | Sherpa → Builder → Sentinel → Judge → Radar | 分解 → 実装 → SAST → レビュー → テスト |
| SPC-800-09 | PR準備 | Guardian → Judge | 変更分析 → レビュー |
| SPC-800-10 | ビジネス/戦略 | CEO → Sherpa → Forge/Builder → Radar | 方針 → 分解 → 実装 → テスト |
| SPC-800-11 | データ分析 | Analyst → CEO → Nexus | 分析 → 意思決定 → 施策化 |

### SPC-801: チェーン選択基準

- タスクの複雑度（SPC-900 Complexity Assessment）に基づいてチェーンを選択
- SIMPLE判定: 短いチェーン（SPC-800-03, SPC-800-06 等）
- COMPLEX判定: 長いチェーン（SPC-800-02, SPC-800-05, SPC-800-08 等）
- セキュリティ関連: 必ず Sentinel を含むチェーンを選択

---

## 10. Complexity Assessment 仕様

### SPC-900: 複雑度判定基準

| ID | 指標 | SIMPLE | COMPLEX |
|----|------|--------|---------|
| SPC-900-01 | 推定ステップ | 1-2 | 3+ |
| SPC-900-02 | 影響ファイル | 1-3 | 4+ |
| SPC-900-03 | セキュリティ関連 | No | Yes |
| SPC-900-04 | 破壊的変更 | No | Yes |

### SPC-901: 判定ルール

- いずれか1つでもCOMPLEXに該当する場合、タスク全体をCOMPLEXと判定する
- COMPLEX判定時は必ずPlanモードで開始し、計画を `.agents/todo.md` に記録する
- SIMPLE判定時はPlanモード任意。ただし失敗時は即座にPlanモードに切り替える

---

## 11. Security by Default 仕様

### SPC-1000: 背景

AI生成コードの45%にOWASP Top 10の脆弱性が含まれる（Veracode調査）。
フレームワーク側でセキュリティを強制し、初心者でも安全なコードを生成する。

### SPC-1001: 実装エージェント必須指示（Builder/Artisan/Forge）

| ID | 指示 | 説明 |
|----|------|------|
| SPC-1001-01 | SQLインジェクション防止 | 文字列結合でのクエリ構築禁止。パラメータバインディング必須 |
| SPC-1001-02 | XSS防止 | ユーザー入力の出力時は必ずエスケープ / サニタイズ |
| SPC-1001-03 | シークレット管理 | 環境変数から読み込み。ハードコード禁止。存在チェック必須 |
| SPC-1001-04 | 入力バリデーション | 型・長さ・形式を検証。ファイルアップロードは拡張子・サイズ・MIMEタイプを制限 |
| SPC-1001-05 | 依存関係安全性 | パッケージ追加時は `npm audit` / `pip audit` 実行。脆弱性パッケージは使用禁止 |
| SPC-1001-06 | エラーハンドリング | スタックトレース・内部情報をユーザーに露出しない |

### SPC-1002: セキュリティレビューチェックリスト（Judge/Auditor 必須確認）

| ID | チェック項目 |
|----|------------|
| SPC-1002-01 | 入力はバリデーションされているか |
| SPC-1002-02 | 出力はエスケープ / サニタイズされているか |
| SPC-1002-03 | SQLクエリはパラメータ化されているか |
| SPC-1002-04 | シークレットはハードコードされていないか |
| SPC-1002-05 | 認証・認可チェックは適切か |
| SPC-1002-06 | エラーハンドリングで機密情報が漏洩していないか |
| SPC-1002-07 | 依存パッケージに既知の脆弱性がないか |

### SPC-1003: RCIループ（Recursive Criticism and Improvement）

AIに自身が生成したコードのセキュリティレビューを依頼すると、脆弱性密度が最大1桁改善する（Stanford研究）。

セキュリティ重要タスクでは以下のループを回す:

```
Builder生成 → Judge セキュリティレビュー → Builder修正 → Sentinel SAST → Radar テスト
```

### SPC-1004: Staged Trust（段階的信頼）

コードが本番に至るまでの各段階にゲートを設ける。

| ID | 段階 | ゲート |
|----|------|-------|
| SPC-1004-01 | Prototype | AI生成コードで素早く検証 |
| SPC-1004-02 | Review | セキュリティ観点のレビュー + RCI実行 |
| SPC-1004-03 | SAST/Test | Sentinel静的解析 + Radar自動テスト通過 |
| SPC-1004-04 | Staging | 本番相当環境での動作確認 |
| SPC-1004-05 | Production | すべてのゲート通過コードのみデプロイ |

### SPC-1005: AI Blind Spot Awareness

AIエージェントが陥りやすい典型的な失敗パターン。全エージェントが自己チェックに使用する。

**コード防御層:**

| ID | 項目 | 説明 |
|----|------|------|
| SPC-1005-01 | SSRF防止 | 外部URL・IPアドレスへの未承認アクセスを許可するコードを生成しない |
| SPC-1005-02 | データ保護 | `.env`、`.secrets/`、`credentials/` への不用意なアクセス・露出を防止 |
| SPC-1005-03 | 入力バリデーション | ユーザー入力を信頼しない。型・長さ・形式を必ず検証 |
| SPC-1005-04 | 破壊的操作防止 | `rm -rf`、`git reset --hard`、`DROP TABLE` 等を安易に生成しない |

**AI判断の制約:**

| ID | 項目 | 説明 |
|----|------|------|
| SPC-1005-05 | 確信度の過大評価 | 「確実」「間違いない」は使わない |
| SPC-1005-06 | ハルシネーション | 存在しないAPI・メソッド・パッケージの実在確認必須 |
| SPC-1005-07 | スコープクリープ | 頼まれていない「改善」を勝手に行わない |

**優先順位:**

| 順位 | 基準 |
|------|------|
| 1 | セキュリティ > 機能 > パフォーマンス > コードの美しさ |
| 2 | 動くコード > 完璧なコード |
| 3 | 既存パターン踏襲 > 新パターン導入 |
| 4 | シンプルな実装 > 抽象化（3行の重複は許容） |
| 5 | 根本原因の修正 > 一時的な回避策 |

---

## 12. 運用仕様

### SPC-1100: Learning Loop

#### SPC-1101: lessons.md フォーマット

プロジェクトごとに `.agents/lessons.md` を管理する。

```
| Date | Chain | Pattern | Lesson | Severity |
|------|-------|---------|--------|----------|
| YYYY-MM-DD | Agent→Agent | 何が起きたか | 学んだこと | high/medium/low |
```

#### SPC-1102: Learning Loop 運用ルール

| ID | ルール | 説明 |
|----|--------|------|
| SPC-1102-01 | 即時記録 | 修正を受けたら即時追記。「保存して」を待たない |
| SPC-1102-02 | dedup | 10件超えたら dedup / condense |
| SPC-1102-03 | 昇格 | high severityパターンは `_framework.md` のルールへの昇格を検討 |
| SPC-1102-04 | セッション開始時レビュー | Context Recovery Protocolの一部として5分レビュー |
| SPC-1102-05 | Reverse Feedback連携 | 下流エージェントから報告された問題も記録 |

### SPC-1200: Quality Gate（必須）

実装完了 → ユーザー報告の前に、以下を必ず通す。

| ID | ゲート | 説明 |
|----|--------|------|
| SPC-1200-01 | テスト2回実行 | 安定性確認（フレーキーテスト検出） |
| SPC-1200-02 | Auditor外部監査 | 設計整合性・セキュリティ・エッジケース |

両方パスしないと「完了」と報告しない。

### SPC-1300: Context Recovery Protocol

コンテキスト圧縮・セッション再開時は、作業開始前に以下を順に実行する。

| ID | ステップ | 説明 |
|----|---------|------|
| SPC-1300-01 | メモリファイル読み込み | ユーザー嗜好・学習内容の復元 |
| SPC-1300-02 | lessons.md レビュー | Learning Loopの失敗・成功パターン確認 |
| SPC-1300-03 | CLAUDE.md 確認 | 現在のプロジェクト設定・ルール確認 |
| SPC-1300-04 | Git状態確認 | `git log --oneline -10` + `git status` で直近の作業状態を把握 |
| SPC-1300-05 | 圧縮サマリー確認 | 圧縮サマリーがあればそれも読む |
| SPC-1300-06 | 実装開始待機 | 上記が完了するまで実装作業に入らない |

### SPC-1400: Memory Management

| ID | ルール | 説明 |
|----|--------|------|
| SPC-1400-01 | MEMORY.md 60行以内 | 詳細はトピック別ファイルにリンク |
| SPC-1400-02 | 即時永続化 | ユーザーの修正・指示は即座にメモリに永続化 |
| SPC-1400-03 | セッション開始時読込 | メモリファイルを読んでから応答開始 |
| SPC-1400-04 | トピック別ファイル | 200行以内を維持 |

### SPC-1500: Progress Reporting

| ID | ルール | 説明 |
|----|--------|------|
| SPC-1500-01 | 沈黙禁止 | 60秒以上沈黙しない |
| SPC-1500-02 | フェーズマーカー | ステップ前後に `[Phase X/Y]` マーカーを表示 |
| SPC-1500-03 | エラー即時表示 | エラーは即座に詳細を表示（握りつぶさない） |

### SPC-1600: Self-Maintenance

| ID | ルール | 説明 |
|----|--------|------|
| SPC-1600-01 | 定期メンテナンス | 10セッションごとにメモリの dedup / condense / prune |
| SPC-1600-02 | Activity Log | 直近20件を保持、古いエントリはアーカイブ |
| SPC-1600-03 | 肥大化防止 | MEMORY.md: 60行、トピックファイル: 200行 |

### SPC-1700: Reverse Feedback

下流 → 上流の品質フィードバック。

**フォーマット:**

```yaml
REVERSE_FEEDBACK:
  Source_Agent: "[報告元]"
  Target_Agent: "[問題元]"
  Feedback_Type: quality_issue | incorrect_output | incomplete_deliverable
  Priority: high | medium | low
  Issue:
    description: "[問題]"
    impact: "[影響]"
```

| Priority | Response |
|----------|----------|
| high | 即時修正 |
| medium | 次サイクル |
| low | バックログ |

### SPC-1800: Shared Knowledge

`.agents/PROJECT.md` に以下を蓄積（全エージェント必須更新）。

| ID | セクション | 説明 |
|----|-----------|------|
| SPC-1800-01 | Architecture Decisions | アーキテクチャに関する決定事項 |
| SPC-1800-02 | Domain Glossary | ドメイン用語集 |
| SPC-1800-03 | Known Gotchas | 既知の落とし穴 |
| SPC-1800-04 | Activity Log | 作業履歴（直近20件） |

**Activity Log フォーマット:**

```
| YYYY-MM-DD | AgentName | (action) | (files) | (outcome) |
```

### SPC-1900: Git Commit & PR

| ID | ルール | 説明 |
|----|--------|------|
| SPC-1900-01 | Conventional Commits | `<type>(<scope>): <description>` 形式 |
| SPC-1900-02 | エージェント名除外 | エージェント名をコミット・PRに含めない |
| SPC-1900-03 | 50文字以内 | コミットメッセージは命令形、50文字以内 |
| SPC-1900-04 | Body | "why" を説明 |
| SPC-1900-05 | ブランチ命名 | `<type>/<short-description>` 形式 |

**Types:** `feat`, `fix`, `docs`, `refactor`, `perf`, `test`, `chore`, `security`

### SPC-2000: Test Policy

| ID | ルール | 説明 |
|----|--------|------|
| SPC-2000-01 | SKIP = FAIL | テストのSKIPは「通った」ではなく「未完了」 |
| SPC-2000-02 | SKIP理由把握 | SKIPの理由を把握し、解消可能なら解消する |
| SPC-2000-03 | SKIPなし報告 | SKIPがあるまま「全テスト通過」と報告しない |

### SPC-2100: Read-only Repository Policy

#### SPC-2101: 4層防御モデル

| Layer | 仕組み | 場所 |
|-------|--------|------|
| L1 | `remote.pushurl = READONLY_NO_PUSH` | 各リポジトリの git config |
| L2 | global pre-push hook | `~/.config/git/hooks/pre-push` |
| L3 | Claude Code deny rules | `settings.json` の deny ルール |
| L4 | フレームワークポリシー | `_framework.md` / CLAUDE.md |

#### SPC-2102: 禁止事項（L4: 即時停止）

| ID | 禁止操作 |
|----|---------|
| SPC-2102-01 | 自プロジェクト以外のリポジトリへの `git push` |
| SPC-2102-02 | 自プロジェクト以外のリポジトリへの `git commit` |
| SPC-2102-03 | 自プロジェクト以外のリポジトリ内のファイル編集 |
| SPC-2102-04 | Read-only リポジトリの remote URL 変更 |
| SPC-2102-05 | Read-only アカウントの PAT を他のリポジトリで使用 |
| SPC-2102-06 | Protected リポジトリのコードを他のリポジトリにコピーして公開 |

#### SPC-2103: 許可事項

| ID | 許可操作 |
|----|---------|
| SPC-2103-01 | `git clone` / `git pull` / `git fetch`（最新コード取得） |
| SPC-2103-02 | コード閲覧・検索（Read, Grep, Glob） |
| SPC-2103-03 | 分析目的でのコード構造・パターンの参照 |

#### SPC-2104: 判定基準

| 条件 | 権限 |
|------|------|
| 作業ディレクトリが自プロジェクトのルート内 | 書き込み可 |
| それ以外 | Read-only（書込操作は全てL4で即時停止） |

### SPC-2200: Critical Thinking Rule

| ID | ルール | 説明 |
|----|--------|------|
| SPC-2200-01 | 鵜呑み禁止 | 指示の矛盾や前提の誤りがあれば指摘する |
| SPC-2200-02 | 根拠必須 | 代替案を出す場合は根拠を付ける |
| SPC-2200-03 | 早期報告 | 前提が崩れたら早期報告 |
| SPC-2200-04 | バランス | 過剰批判で手が止まるのは禁止 |
| SPC-2200-05 | 自問 | 「本当にそうか？」を常に自問。特に数値計算・見積もり・因果推論 |

### SPC-2300: Coordinator Protocols

| ID | プロトコル | 説明 |
|----|-----------|------|
| SPC-2300-01 | コーディネーターはコードを書かない | 計画 → 委任 → レビューが仕事 |
| SPC-2300-02 | 全成果物レビュー | レビュー後にユーザーに報告 |
| SPC-2300-03 | 実装後検証 | テスト + パイプライン実行 + 出力目視確認まで行う |
| SPC-2300-04 | ワークフロー自動化 | 同じ手順を2回以上実行したらスラッシュコマンド化を提案 |

---

## 変更履歴

| バージョン | 日付 | 変更内容 |
|-----------|------|---------|
| 1.0.0 | 2026-02-27 | 初版作成 |
