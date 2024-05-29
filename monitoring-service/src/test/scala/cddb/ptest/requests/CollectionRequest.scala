package cddb.ptest.requests

import scala.concurrent.duration._

import io.gatling.core.Predef._
import io.gatling.http.Predef._

object CollectionRequest {

  val getCollectionFromUser = http("Get Collection from User")
    .get("/api/collections")

  val addCardToCollection = http("Add Card to Collection")
    .post("/api/collections/")
    .body(StringBody("""{ "oracle_id": "${oracle_id}", "print_id": "${print_id}", "condition": "MINT" }""")).asJson
    .check(
      status.is(201),
      jsonPath("$.CardInstanceId").saveAs("CardInstanceId")
    )

}