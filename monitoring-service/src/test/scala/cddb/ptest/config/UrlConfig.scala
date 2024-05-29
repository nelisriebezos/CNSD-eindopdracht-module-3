package cddb.ptest.config

import cddb.ptest.utils.SSMParameterStore.retrieveParameterValue

object UrlConfig {
  val stage: String = System.getProperty("Stage", "development")

  val baseUrl: String = retrieveParameterValue(s"/$stage/frontEnd/cloudFrontUrl")
}