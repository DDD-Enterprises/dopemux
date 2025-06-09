
def export_markdown(csv_path, out_md_path):
    import pandas as pd
    df = pd.read_csv(csv_path)
    md_blocks = []
    for _, row in df.iterrows():
        md = f'''## 🔄 Project: {row['project']} @ {row['release']} ({row['date']})
**Session:** {row['session_id']}
**Summary:** {row['summary']}

**Key Decisions:** {row['decisions']}
**Architecture/Specs:** {row['architecture']}

**Code Snippets:**\n{row['code_snippets']}

**Bugs, TODOs:** {row['bugs']}
**Tools:** {row['tools']}
**Tags:** {row['tags']}
**Related Projects:** {row['related_projects']}
**Artifacts:** {row['files_artifacts']}
**Context Ref:** {row['context_ref']}
**Extra:** {row['extra']}
**Schema:** {row['schema_version']}
'''
        md_blocks.append(md)
    with open(out_md_path, 'w') as f:
        f.write('\n\n'.join(md_blocks))
    print(f"Markdown exported to {out_md_path}")
