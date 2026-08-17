import { NextResponse } from "next/server";
import clientPromise from "@/lib/mongodb";

type ClickDoc = { _id: string; count: number };

const COLLECTION = "linkClicks";

export async function GET() {
  const client = await clientPromise;
  const docs = await client
    .db()
    .collection<ClickDoc>(COLLECTION)
    .find({})
    .toArray();

  const counts = Object.fromEntries(docs.map((doc) => [doc._id, doc.count]));
  return NextResponse.json(counts);
}

export async function POST(request: Request) {
  const { id } = await request.json();

  if (typeof id !== "string" || !id) {
    return NextResponse.json({ error: "invalid id" }, { status: 400 });
  }

  const client = await clientPromise;
  const result = await client
    .db()
    .collection<ClickDoc>(COLLECTION)
    .findOneAndUpdate(
      { _id: id },
      { $inc: { count: 1 } },
      { upsert: true, returnDocument: "after" }
    );

  return NextResponse.json({ id, count: result?.count ?? 1 });
}
