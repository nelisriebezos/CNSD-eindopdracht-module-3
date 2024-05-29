export type PrintCard = {
  PK: string,
  SK: string,
  OracleId: string,
  OracleName: string,
  PrintId: string,
  Price: number | null,
  ReleasedAt: string,
  SetName: string,
  Rarity: "common" | "uncommon" | "rare" | "mythic",
  CardFaces: PrintFace[],
}

export type PrintFace = {
  Colors: string[],
  FaceName: string,
  FlavorText: string,
  ImageUrl: string,
  ManaCost: string,
  OracleText: string,
  TypeLine: string,
}

export type DeckCard = {
  PK: string,
  SK: string,
  card_location: string,
  CardFaces: CardFace[]
  data_type: string,
  deck_card_id: string,
  deck_id: string,
  OracleId: string,
  OracleName: string,
  Price: number,
  PrintId: string,
  Rarity: string,
  ReleasedAt: string,
  SetName: string,
  user_id: string
  card_instance_id?: string
}

export type CardFace = {
  Colors: string[],
  FlavorText: string,
  ManaCost: string,
  TypeLine: string,
  ImageUrl?: string,
  FaceName: string,
  OracleText: string
}

export type CollectionPrintCard = {
  PK: string,
  SK: string,
  GSI1SK: string | undefined,
  GSI2SK: string | undefined,
  CardInstanceId: string,
  Condition: string,
  DeckId: string,
  OracleId: string,
  OracleName: string,
  PrintId: string,
  Price: number | null,
  ReleasedAt: string,
  SetName: string,
  Rarity: "common" | "uncommon" | "rare" | "mythic",
  CardFaces: CollectionPrintFace[],
}

export type CollectionPrintFace = {
  Colors: string[],
  FaceName: string,
  FlavorText: string,
  ImageUrl: string,
  ManaCost: string,
  OracleText: string,
  TypeLine: string,
}

export type CardInstance =
{
  "CardFaces": CardFace[],
  "CardInstanceId": string,
  "Condition": string,
  "OracleId": string,
  "OracleName": string,
  "Price": string,
  "PrintId": string,
  "Rarity": string,
  "ReleasedAt": string,
  "SetName": string,
}