package cddb.ptest.utils

import software.amazon.awssdk.services.ssm.SsmClient
import software.amazon.awssdk.services.ssm.model.GetParameterRequest

object SSMParameterStore {
  private val ssmClient: SsmClient = SsmClient.create()

  def retrieveParameterValue(parameterName: String): String = {
    println(s"Retrieving parameter: $parameterName")
    val request = GetParameterRequest.builder()
      .name(parameterName)
      .build()

    try {
      val response = ssmClient.getParameter(request)
      response.parameter().value()
    } catch {
      case e: Exception =>
        println(s"Error retrieving parameter: $e")
        throw e
    }
  }
}