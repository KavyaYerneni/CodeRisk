# Ethics and responsible use

## Purpose

CodeRisk is a research / engineering prototype for **prioritizing** review attention. It is not an automated merge blocker and must not be treated as proof of safety.

## Risks

- **False confidence:** Low risk scores can still hide severe bugs.
- **Bias:** Author tenure and activity features can correlate with seniority or team structure.
- **Label noise:** SZZ and synthetic labels mis-teach models; errors can concentrate on certain file types or repos.
- **Privacy:** Mined diffs may contain secrets or proprietary code — keep raw data out of git and shared artifacts.

## Practices

1. Keep humans in the loop for merge decisions.
2. Document dataset source (`synthetic_demo` vs mined) on every metrics report.
3. Prefer measured numbers only in public claims.
4. Rotate and scope `GITHUB_TOKEN`; never commit it.
5. Disclose limitations alongside any demo metrics.
