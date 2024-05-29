package cddb.ptest.requests

import scala.concurrent.duration._

import io.gatling.core.Predef._
import io.gatling.http.Predef._

object UserRequest {

  def createUserRequest(requestName: String) = {
    http(requestName)
      .post("/api/users")
      .body(StringBody("""{ "password": "${password}", "email": "${email}" }""")).asJson
  }

  val register = createUserRequest("Register User")
  
  val existingRegister = createUserRequest("Existing Register User")

  val login = http("Login user")
    .post("/api/users/login")
    .body(StringBody("""{ "password": "${password}", "email": "${email}" }""")).asJson
    .check(
      status.is(200),
      jsonPath("$.token").saveAs("authToken")
    )
}