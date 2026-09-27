"""Builds a compact Africa/MENA skill-demand file from lukebarousse/data_jobs (HF, Apache-2.0).
Run: python data/prepare_data.py   (from gomycode-2026 folder)"""
import ast, json
import pandas as pd

d = pd.read_csv("data/data_jobs.csv", usecols=["job_title_short", "job_title", "job_country",
                                               "job_skills", "job_no_degree_mention"])
countries = ["Kenya", "Nigeria", "Tunisia", "Morocco", "Algeria", "Senegal", "Côte d'Ivoire",
             "Saudi Arabia", "Egypt", "South Africa"]
d = d[d.job_skills.notna()].copy()
d["skills"] = d.job_skills.apply(ast.literal_eval)
a = d[d.job_country.isin(countries)]

out = {"source": "lukebarousse/data_jobs (Hugging Face, Apache-2.0), 2023 job postings",
       "countries": {}, "roles": {}}
for c, g in a.groupby("job_country"):
    out["countries"][c] = {"postings": int(len(g)),
                           "no_degree_pct": round(100 * float(g.job_no_degree_mention.mean()), 1)}
for r, g in a.groupby("job_title_short"):
    e = g.explode("skills")
    vc = (e.skills.value_counts() / len(g) * 100).round(1).head(15)
    out["roles"][r] = {"postings": int(len(g)), "top_skills_pct": vc.to_dict()}

json.dump(out, open("data/africa_skill_demand.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
a.drop(columns=["job_skills"]).to_json("data/africa_jobs_subset.jsonl", orient="records", lines=True, force_ascii=False)
print(len(a), json.dumps(out["countries"], ensure_ascii=False))
for r in out["roles"]:
    print(r, out["roles"][r]["postings"], list(out["roles"][r]["top_skills_pct"].items())[:6])
