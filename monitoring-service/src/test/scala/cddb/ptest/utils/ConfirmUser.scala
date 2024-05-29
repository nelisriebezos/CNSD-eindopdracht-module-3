package cddb.ptest.utils

import com.amazonaws.services.cognitoidp.AWSCognitoIdentityProvider
import com.amazonaws.services.cognitoidp.AWSCognitoIdentityProviderClientBuilder
import com.amazonaws.services.cognitoidp.model.AdminConfirmSignUpRequest

import cddb.ptest.utils.SSMParameterStore.retrieveParameterValue

object ConfirmUser {
  private val cognitoClient: AWSCognitoIdentityProvider = AWSCognitoIdentityProviderClientBuilder.defaultClient()
  
  val stage: String = System.getProperty("Stage", "development")
  val userPoolId: String = retrieveParameterValue(s"/$stage/Cognito/userPoolId")

  def adminConfirmUser(username: String) = {
    val confirmRequest = new AdminConfirmSignUpRequest()
      .withUsername(username)
      .withUserPoolId(userPoolId)

    cognitoClient.adminConfirmSignUp(confirmRequest)
  }
}