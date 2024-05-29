package cddb.ptest.scenarios

import scala.concurrent.duration._
import scala.util.Random
import scala.collection.mutable.ListBuffer

import cddb.ptest.requests.UserRequest
import cddb.ptest.requests.CollectionRequest

import cddb.ptest.utils.ConfirmUser

import io.gatling.core.feeder.Feeder
import io.gatling.core.Predef._
import io.gatling.http.Predef._

object Scenarios {

  private val credentialsFeeder = Iterator.continually({
    val randomString = Random.alphanumeric.take(8).mkString
      Map("password" -> randomString, "email" -> (s"p-test@$randomString.com"))
  })

  private val existingUserFeeder = Iterator.continually(Map(
    "password" -> "existingPassword",
    "email" -> "existing@mail.com"
  ))

  private val cardFeeder = jsonFile("src/test/resources/bodies/cards.json").shuffle

  private val addCardsToCollectionScenario = repeat(5) {
    feed(cardFeeder)
      .exec(CollectionRequest.addCardToCollection.header("Authorization", "Bearer ${authToken}").check(status.is(201)))
      .pause(50 millis)
  }

  private val deckNameFeeder = Iterator.continually(Map(
    "deckname" -> Random.alphanumeric.take(8).mkString
  ))

  // Registration, Confirmation, Login, Collection, Deck and Cards Scenario
  val registerLoginCollectionAndCardsScenario = scenario("Registration, Confirmation, Login, Collection, Deck and Cards Scenario")
    .feed(credentialsFeeder)

    // Register and confirm user
    .exec(UserRequest.register.check(status.is(201)))
    .exec(session => {
      val email = session("email").as[String]
      ConfirmUser.adminConfirmUser(email)
      session
    })
    .pause(50 millis)

    // Login user and extract token
    .exec(UserRequest.login)
    .pause(200 millis)

    // Add to and get collection
    .exec(CollectionRequest.getCollectionFromUser.header("Authorization", "Bearer ${authToken}").check(status.is(200)))
    .exec(addCardsToCollectionScenario)
    .pause(50 millis)
    .exec(CollectionRequest.getCollectionFromUser.header("Authorization", "Bearer ${authToken}").check(status.is(200)))

  // Register Existing User Scenario
  val existingUserScenario = scenario("Register Existing User")

    // Register existing users
    .feed(existingUserFeeder)
    .exec(
      exec(session => {
        if (!session.contains("registered")) {
          UserRequest.existingRegister.check(status.is(201))
          session.set("registered", true)
        } else {
          UserRequest.existingRegister.check(status.is(409))
          session
        }
      })
    )
}