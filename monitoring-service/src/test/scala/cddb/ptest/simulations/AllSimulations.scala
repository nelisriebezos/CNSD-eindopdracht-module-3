package cddb.ptest.simulations

import scala.concurrent.duration._

import io.gatling.core.Predef._
import io.gatling.http.Predef._
import io.gatling.jdbc.Predef._

import cddb.ptest.scenarios.Scenarios._
import cddb.ptest.config.UrlConfig.baseUrl


class AllSimulations extends Simulation {

  val levelDuration = System.getProperty("levelDuration", "3").toInt seconds
  val rampDuration = System.getProperty("rampDuration", "2").toInt seconds
  val userIncrease = System.getProperty("userIncrease", "1").toDouble
  val levels = System.getProperty("levels", "3").toInt
  val startingRate = System.getProperty("startingRate", "1").toDouble

  val pauseDuration = 1

  def httpProtocol = http.baseUrl(baseUrl).userAgentHeader("Gatling/test")

  val users = incrementUsersPerSec(userIncrease)
               .times(levels)
               .eachLevelLasting(levelDuration)
               .separatedByRampsLasting(rampDuration)
               .startingFrom(startingRate)

  setUp(
    registerLoginCollectionAndCardsScenario.inject(users),
    existingUserScenario.inject(users)
  ).protocols(httpProtocol)
}