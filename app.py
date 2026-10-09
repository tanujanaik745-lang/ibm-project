import warnings
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

warnings.filterwarnings("ignore")
st.set_page_config(page_title="Retail BI & Customer Risk Analytics", page_icon="📊", layout="wide")

st.markdown("""
<style>
.block-container{padding-top:1.2rem}
.hero{padding:1.2rem 1.5rem;border-radius:14px;background:linear-gradient(120deg,#111827,#334155);color:white}
.hero h1{color:white}.hero p{color:#e5e7eb}
div[data-testid="stMetric"]{border:1px solid #80808044;padding:12px;border-radius:12px}
</style>
<div class="hero"><h1>📊 Retail Business Intelligence & Customer Risk Analytics</h1>
<p>Convert raw data into KPIs, trends, drivers, risks, opportunities, and business actions.</p></div>
""", unsafe_allow_html=True)

def demo_data():
    rng=np.random.default_rng(42); n=650
    dates=pd.date_range("2024-01-01","2025-12-31",freq="D")
    category=rng.choice(["Electronics","Home","Fashion","Beauty","Grocery"],n)
    region=rng.choice(["West","North","South","East","Central"],n)
    qty=rng.integers(1,6,n)
    base={"Electronics":7800,"Home":2400,"Fashion":1300,"Beauty":850,"Grocery":500}
    price=np.array([base[x] for x in category])*rng.uniform(.45,1.7,n)
    revenue=qty*price*(1-rng.choice([0,.05,.1,.15,.2],n))
    cost=revenue*rng.uniform(.52,.86,n)
    days=rng.integers(1,180,n)
    churn=(rng.random(n)<(.1+(days>100)*.3+(region=="West")*.12)).astype(int)
    df=pd.DataFrame({"order_id":[f"ORD-{i+1:05d}" for i in range(n)],
        "order_date":rng.choice(dates,n),"customer_id":rng.integers(1001,1280,n),
        "region":region,"category":category,"quantity":qty,"unit_price":price.round(2),
        "revenue":revenue.round(2),"cost":cost.round(2),"profit":(revenue-cost).round(2),
        "days_since_last_order":days,"churned":churn})
    df.loc[[1,5,12],"region"]=None
    return pd.concat([df,df.iloc[[2,11]]],ignore_index=True)

def load_file(f):
    if f.name.lower().endswith(".csv"):
        try: return pd.read_csv(f)
        except UnicodeDecodeError:
            f.seek(0); return pd.read_csv(f,encoding="latin-1")
    return pd.read_excel(f)

def clean_data(raw):
    df=raw.copy()
    df.columns=[str(c).strip() for c in df.columns]
    before=len(df); df=df.drop_duplicates()
    removed=before-len(df)
    for c in df.columns:
        if df[c].dtype=="object" and any(k in c.lower() for k in ("date","time","timestamp")):
            parsed=pd.to_datetime(df[c],errors="coerce")
            if parsed.notna().mean()>.55: df[c]=parsed
    for c in df.select_dtypes(include="object").columns:
        s=df[c].astype(str).str.replace(",","",regex=False).str.replace("$","",regex=False)
        parsed=pd.to_numeric(s,errors="coerce")
        if df[c].notna().sum() and parsed.notna().sum()/df[c].notna().sum()>=.85: df[c]=parsed
    missing=int(df.isna().sum().sum())
    for c in df.columns:
        if pd.api.types.is_numeric_dtype(df[c]):
            if df[c].notna().any(): df[c]=df[c].fillna(df[c].median())
        elif not pd.api.types.is_datetime64_any_dtype(df[c]):
            mode=df[c].mode(dropna=True)
            df[c]=df[c].fillna(mode.iloc[0] if len(mode) else "Unknown")
    return df,removed,missing

def guess(cols,keys):
    for c in cols:
        if any(k in c.lower().replace("_"," ") for k in keys): return c
    return "None"

def fmt(x):
    try: return f"{x:,.2f}" if abs(float(x))<1000 else f"{x:,.0f}"
    except: return str(x)

with st.sidebar:
    st.header("Data workspace")
    source=st.radio("Data source",["Synthetic demo data","Upload my dataset"])
    uploaded=st.file_uploader("Upload CSV or Excel",type=["csv","xlsx","xls"]) if source=="Upload my dataset" else None
    st.caption("For final submission, use a dataset different from the exact internship masterclass dataset.")

if source=="Upload my dataset" and uploaded is None:
    st.info("Upload a CSV/XLSX dataset in the sidebar, or choose Synthetic demo data.")
    st.stop()
try:
    raw=demo_data() if source=="Synthetic demo data" else load_file(uploaded)
except Exception as e:
    st.error(f"Could not read file: {e}"); st.stop()
if raw.empty:
    st.error("Dataset has no rows."); st.stop()

df,duplicates_removed,missing_before=clean_data(raw)
all_cols=df.columns.tolist()
numeric=df.select_dtypes(include=np.number).columns.tolist()
categorical=[c for c in all_cols if c not in numeric and not pd.api.types.is_datetime64_any_dtype(df[c])]
with st.sidebar:
    st.divider(); st.subheader("Map dataset fields")
    date_options=["None"]+all_cols
    date_guess=guess(all_cols,["date","time","timestamp"])
    date_col=st.selectbox("Date/time",date_options,index=date_options.index(date_guess) if date_guess in date_options else 0)
    value_options=["None"]+numeric
    val_guess=guess(numeric,["revenue","sales","amount","total","value","spend","price"])
    value_col=st.selectbox("Main value / sales",value_options,index=value_options.index(val_guess) if val_guess in value_options else 0)
    profit_guess=guess(numeric,["profit","margin"])
    profit_col=st.selectbox("Profit (optional)",value_options,index=value_options.index(profit_guess) if profit_guess in value_options else 0)
    cat_options=["None"]+categorical
    cat_guess=guess(categorical,["category","product","item","segment","type"])
    category_col=st.selectbox("Category/product",cat_options,index=cat_options.index(cat_guess) if cat_guess in cat_options else 0)
    region_guess=guess(categorical,["region","state","city","country","location","market"])
    region_col=st.selectbox("Region/location",cat_options,index=cat_options.index(region_guess) if region_guess in cat_options else 0)
    customer_guess=guess(all_cols,["customer id","customer","client","user id"])
    customer_col=st.selectbox("Customer/entity ID",["None"]+all_cols,index=(["None"]+all_cols).index(customer_guess) if customer_guess in ["None"]+all_cols else 0)
    risk_guess=guess(numeric,["risk","churn","fraud","default","days since"])
    risk_col=st.selectbox("Risk indicator (optional)",value_options,index=value_options.index(risk_guess) if risk_guess in value_options else 0)

date_col=None if date_col=="None" else date_col
value_col=None if value_col=="None" else value_col
profit_col=None if profit_col=="None" else profit_col
category_col=None if category_col=="None" else category_col
region_col=None if region_col=="None" else region_col
customer_col=None if customer_col=="None" else customer_col
risk_col=None if risk_col=="None" else risk_col

tabs=st.tabs(["Executive Overview","Sales & Product Analysis","Customer & Risk Analysis","Data Quality","Explore Data"])

with tabs[0]:
    st.subheader("Executive overview")
    a,b,c,d=st.columns(4)
    a.metric("Records",f"{len(df):,}",f"{duplicates_removed} duplicates removed")
    b.metric("Fields",f"{len(df.columns):,}")
    if value_col:
        a_value=pd.to_numeric(df[value_col],errors="coerce")
        c.metric(f"Total {value_col}",fmt(a_value.sum()))
        d.metric(f"Average {value_col}",fmt(a_value.mean()))
    else:
        c.metric("Numeric fields",len(numeric)); d.metric("Categorical fields",len(categorical))
    left,right=st.columns([1.5,1])
    with left:
        st.markdown("#### Performance trend")
        if date_col and value_col:
            t=df[[date_col,value_col]].copy()
            t[date_col]=pd.to_datetime(t[date_col],errors="coerce")
            t[value_col]=pd.to_numeric(t[value_col],errors="coerce")
            t=t.dropna()
            if len(t):
                t=t.set_index(date_col).resample("MS")[value_col].sum().reset_index()
                st.plotly_chart(px.line(t,x=date_col,y=value_col,markers=True,title=f"Monthly {value_col}"),use_container_width=True)
        elif category_col and value_col:
            t=df.groupby(category_col,as_index=False)[value_col].sum().sort_values(value_col,ascending=False)
            st.plotly_chart(px.bar(t,x=category_col,y=value_col,title=f"{value_col} by {category_col}"),use_container_width=True)
        else: st.info("Select date/value or category/value fields in the sidebar.")
    with right:
        st.markdown("#### KPI snapshot")
        if category_col and value_col:
            g=df.groupby(category_col)[value_col].sum().sort_values(ascending=False)
            if len(g): st.metric("Top category",str(g.index[0])); st.metric("Top category value",fmt(g.iloc[0]))
        if region_col and value_col:
            g=df.groupby(region_col)[value_col].sum().sort_values(ascending=False)
            if len(g): st.metric("Leading region",str(g.index[0]))
        if profit_col and value_col:
            total=pd.to_numeric(df[value_col],errors="coerce").sum()
            profit=pd.to_numeric(df[profit_col],errors="coerce").sum()
            st.metric("Profit / value (%)",f"{profit/total*100:.1f}%" if total else "N/A")
    st.markdown("#### Facts → insights → actions")
    insights=[]
    if value_col:
        total=pd.to_numeric(df[value_col],errors="coerce").sum()
        insights.append(("Fact",f"Total **{value_col}** is **{fmt(total)}** across {len(df):,} records."))
        if date_col:
            t=df[[date_col,value_col]].copy(); t[date_col]=pd.to_datetime(t[date_col],errors="coerce")
            t[value_col]=pd.to_numeric(t[value_col],errors="coerce"); t=t.dropna().set_index(date_col).resample("MS")[value_col].sum()
            if len(t)>1:
                change=(t.iloc[-1]-t.iloc[0])/abs(t.iloc[0])*100 if t.iloc[0] else np.nan
                insights.append(("Trend",f"Monthly value changed from {fmt(t.iloc[0])} to {fmt(t.iloc[-1])}"+(f" ({change:+.1f}%)." if pd.notna(change) else ".")))
        if category_col:
            g=df.groupby(category_col)[value_col].sum().sort_values(ascending=False)
            if len(g):
                share=g.iloc[0]/g.sum()*100 if g.sum() else 0
                insights.append(("Opportunity",f"**{g.index[0]}** leads by {value_col}, contributing {share:.1f}% of the total. Check its margin, stock, and demand before increasing investment."))
                if len(g)>1: insights.append(("Action",f"Review **{g.index[-1]}** for pricing, demand, availability, and marketing efficiency before deciding how to improve performance."))
        if region_col:
            g=df.groupby(region_col)[value_col].sum().sort_values(ascending=False)
            if len(g)>1: insights.append(("Driver",f"**{g.index[0]}** has the highest total {value_col}. Compare its product mix and order/customer profile with lower-performing regions."))
    if profit_col and value_col:
        total=pd.to_numeric(df[value_col],errors="coerce").sum(); profit=pd.to_numeric(df[profit_col],errors="coerce").sum()
        if total: insights.append(("Risk",f"Selected profit/value ratio is {profit/total*100:.1f}%. Validate whether the selected fields use compatible definitions."))
    if risk_col:
        vals=pd.to_numeric(df[risk_col],errors="coerce").dropna()
        if len(vals):
            cut=vals.quantile(.75)
            insights.append(("Risk",f"{int((vals>=cut).sum()):,} records are at or above the 75th percentile of **{risk_col}**. Review the segment and validate the risk definition."))
    if not insights: insights=[("Next step","Map relevant columns in the sidebar to generate dataset-specific insights.")]
    for label,msg in insights: st.markdown(f"**{label}:** {msg}")

with tabs[1]:
    st.subheader("Sales & product analysis")
    if category_col and value_col:
        g=df.groupby(category_col,as_index=False)[value_col].sum().sort_values(value_col,ascending=False)
        x,y=st.columns(2)
        x.plotly_chart(px.bar(g,x=category_col,y=value_col,color=category_col,title=f"{value_col} by category"),use_container_width=True)
        y.plotly_chart(px.pie(g,names=category_col,values=value_col,hole=.4,title="Category contribution"),use_container_width=True)
        if profit_col:
            p=df.groupby(category_col,as_index=False)[[value_col,profit_col]].sum()
            p["Margin (%)"]=np.where(p[value_col]!=0,p[profit_col]/p[value_col]*100,np.nan)
            st.markdown("#### Category profitability"); st.dataframe(p,use_container_width=True,hide_index=True)
            st.plotly_chart(px.bar(p,x=category_col,y="Margin (%)",title="Profit/value ratio by category"),use_container_width=True)
    else: st.info("Select category and main value fields to view this analysis.")
    if region_col and value_col:
        g=df.groupby(region_col,as_index=False)[value_col].sum().sort_values(value_col,ascending=False)
        st.plotly_chart(px.bar(g,x=region_col,y=value_col,title=f"{value_col} by region"),use_container_width=True)
    if date_col and value_col:
        t=df[[date_col,value_col]].copy(); t[date_col]=pd.to_datetime(t[date_col],errors="coerce"); t[value_col]=pd.to_numeric(t[value_col],errors="coerce"); t=t.dropna()
        if len(t):
            t["Month"]=t[date_col].dt.month_name()
            order=["January","February","March","April","May","June","July","August","September","October","November","December"]
            g=t.groupby("Month",as_index=False)[value_col].mean(); g["order"]=g["Month"].map({v:i for i,v in enumerate(order)}); g=g.sort_values("order")
            st.plotly_chart(px.line(g,x="Month",y=value_col,markers=True,title="Average value by month name"),use_container_width=True)

with tabs[2]:
    st.subheader("Customer & risk analysis")
    if customer_col: st.metric("Unique customers/entities",f"{df[customer_col].nunique():,}")
    if risk_col:
        vals=pd.to_numeric(df[risk_col],errors="coerce"); valid=vals.dropna()
        if len(valid):
            cutoff=valid.quantile(.75); high=df.loc[vals>=cutoff].copy()
            a,b,c=st.columns(3); a.metric("75th percentile",fmt(cutoff)); b.metric("High-risk records",f"{len(high):,}"); c.metric("High-risk share",f"{len(high)/len(df)*100:.1f}%")
            st.caption("This is a percentile-based screening rule, not a validated prediction or diagnosis.")
            if region_col:
                g=df.assign(_risk=vals).groupby(region_col,as_index=False)["_risk"].mean().sort_values("_risk",ascending=False)
                st.plotly_chart(px.bar(g,x=region_col,y="_risk",title=f"Average {risk_col} by region"),use_container_width=True)
            if category_col:
                g=df.assign(_risk=vals).groupby(category_col,as_index=False)["_risk"].mean().sort_values("_risk",ascending=False)
                st.plotly_chart(px.bar(g,x=category_col,y="_risk",title=f"Average {risk_col} by category"),use_container_width=True)
            st.markdown("#### Records for review"); st.dataframe(high.head(100),use_container_width=True,hide_index=True)
            st.download_button("Download high-risk records",high.to_csv(index=False).encode(),file_name="high_risk_records.csv",mime="text/csv")
        else: st.info("Risk field has no numeric values.")
    else: st.info("Choose a numeric risk/churn/fraud indicator in the sidebar. The app will not invent a risk field.")
    st.markdown("**Suggested risk response**")
    st.write("1. Validate the risk indicator. 2. Review flagged records with business context. 3. Investigate possible drivers. 4. Test a small measurable intervention. 5. Monitor results.")

with tabs[3]:
    st.subheader("Data quality & cleaning")
    a,b,c,d=st.columns(4); a.metric("Original rows",f"{len(raw):,}"); b.metric("Cleaned rows",f"{len(df):,}"); c.metric("Duplicates removed",duplicates_removed); d.metric("Missing cells before fill",missing_before)
    profile=pd.DataFrame({"Column":df.columns,"Data type":[str(df[x].dtype) for x in df.columns],
        "Missing after cleaning":[int(df[x].isna().sum()) for x in df.columns],
        "Unique values":[int(df[x].nunique(dropna=True)) for x in df.columns],
        "Sample value":[str(df[x].dropna().iloc[0])[:60] if df[x].notna().any() else "—" for x in df.columns]})
    st.dataframe(profile,use_container_width=True,hide_index=True)
    st.markdown("**Cleaning actions**")
    st.write("- Removed exact duplicate rows and trimmed column-name whitespace.")
    st.write("- Converted likely date columns and numeric-looking text where enough values parsed.")
    st.write("- Filled missing numeric values with median and categorical values with mode where possible.")
    st.warning("Review the cleaning results before formal reporting. Imputation can affect distributions; missing dates are not fabricated.")

with tabs[4]:
    st.subheader("Explore data")
    st.dataframe(df.head(300),use_container_width=True,hide_index=True)
    st.download_button("Download cleaned dataset (CSV)",df.to_csv(index=False).encode(),file_name="cleaned_dataset.csv",mime="text/csv")
    if numeric:
        st.markdown("#### Descriptive statistics"); st.dataframe(df[numeric].describe().T,use_container_width=True)
        if len(numeric)>1:
            st.plotly_chart(px.imshow(df[numeric].corr(numeric_only=True),text_auto=".2f",aspect="auto",title="Numeric correlation heatmap"),use_container_width=True)
    if categorical:
        chosen=st.selectbox("Inspect category counts",categorical)
        counts=df[chosen].astype(str).value_counts().head(20).rename_axis(chosen).reset_index(name="Count")
        st.plotly_chart(px.bar(counts,x=chosen,y="Count",title=f"Top values in {chosen}"),use_container_width=True)

st.divider()
st.caption("This version uses rule-based analytical insights, not an external generative-AI API. Verify all findings against the real business context before acting.")
