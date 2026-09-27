"""Does local demand differ from global demand? (the 'why not ChatGPT' test)"""
import ast
import pandas as pd

d = pd.read_csv("data/data_jobs.csv", usecols=["job_title_short", "job_country", "job_skills"])
d = d[d.job_skills.notna()].copy()
d["skills"] = d.job_skills.apply(ast.literal_eval)


def top(g, n=12):
    return (g.explode("skills").skills.value_counts() / len(g) * 100).round(1).head(n)


for role in ["Data Analyst", "Software Engineer", "Data Engineer"]:
    r = d[d.job_title_short == role]
    us, ke = r[r.job_country == "United States"], r[r.job_country == "Kenya"]
    t = pd.DataFrame({"US": top(us, 25), "Kenya": top(ke, 25)}).fillna(0)
    t["diff"] = t.Kenya - t.US
    print(f"\n== {role}: US n={len(us)}  Kenya n={len(ke)}")
    print(t.sort_values("Kenya", ascending=False).head(14).to_string())
