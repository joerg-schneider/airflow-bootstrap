import pyspark
import pyspark.sql.functions as f

from airtunnel import PySparkDataAsset, PySparkDataAssetIO


def rebuild_for_store(asset: PySparkDataAsset, airflow_context):
    student = PySparkDataAsset(name="student_pyspark")
    programme = PySparkDataAsset(name="programme_pyspark")
    enrollment = PySparkDataAsset(name="enrollment_pyspark")

    student_df = student.retrieve_from_store(
        airflow_context=airflow_context, consuming_asset=asset
    )
    programme_df = programme.retrieve_from_store(
        airflow_context=airflow_context, consuming_asset=asset
    )

    enrollment_df = enrollment.retrieve_from_store(
        airflow_context=airflow_context, consuming_asset=asset
    )

    enrollment_summary: pyspark.sql.DataFrame = enrollment_df.join(
        other=student_df, on=student.declarations.key_columns
    ).join(other=programme_df, on=programme.declarations.key_columns)

    enrollment_summary = (
        enrollment_summary.select(["student_major", "programme_name", "student_id"])
        .groupby(["student_major", "programme_name"])
        .agg(f.count('*'))
    )

    PySparkDataAssetIO.write_data_asset(asset=asset, data=enrollment_summary)
