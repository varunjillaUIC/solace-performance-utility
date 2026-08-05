import client from "./client";
import { Profile } from "../types/index";

export const getProfiles = () =>
  client.get<Profile[]>("/profiles");

export const saveProfile = (profile: Profile) =>
  client.post("/profiles", profile);

export const deleteProfile = (name: string) =>
  client.delete(`/profiles/${name}`);